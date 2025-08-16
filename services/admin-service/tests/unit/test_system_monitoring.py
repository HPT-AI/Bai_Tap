"""
Unit tests for System Monitoring functionality.
"""

import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock, patch

import psutil
import pytest

# Mock imports - these would be actual imports in real implementation
# from admin_service.services import SystemMonitoringService, AlertService
# from admin_service.models import SystemMetric, Alert, HealthCheck
# from admin_service.schemas import SystemStatus, MetricData


@pytest.mark.asyncio
class TestSystemMetrics:
    """Test system metrics collection and analysis."""

    def test_collect_cpu_metrics(self, mock_system_data):
        """Test CPU metrics collection."""

        def collect_cpu_metrics():
            """
            Collect CPU usage metrics
            """
            try:
                # Mock psutil.cpu_percent() behavior
                cpu_percent = 45.2
                cpu_count = 8
                cpu_freq = 2400.0  # MHz
                load_avg = [1.2, 1.5, 1.8]  # 1, 5, 15 minute averages

                # Calculate per-core usage (mock data)
                per_core_usage = [42.1, 48.3, 44.7, 46.9, 43.2, 47.1, 45.8, 44.5]

                metrics = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "cpu_percent": cpu_percent,
                    "cpu_count": cpu_count,
                    "cpu_frequency": cpu_freq,
                    "load_average": {
                        "1min": load_avg[0],
                        "5min": load_avg[1],
                        "15min": load_avg[2],
                    },
                    "per_core_usage": per_core_usage,
                    "status": "normal"
                    if cpu_percent < 80
                    else "warning"
                    if cpu_percent < 90
                    else "critical",
                }

                # Add alerts if necessary
                alerts = []
                if cpu_percent > 90:
                    alerts.append(
                        {
                            "level": "critical",
                            "message": f"CPU usage is critically high: {cpu_percent}%",
                            "threshold": 90,
                        }
                    )
                elif cpu_percent > 80:
                    alerts.append(
                        {
                            "level": "warning",
                            "message": f"CPU usage is high: {cpu_percent}%",
                            "threshold": 80,
                        }
                    )

                if load_avg[0] > cpu_count:
                    alerts.append(
                        {
                            "level": "warning",
                            "message": f"Load average is high: {load_avg[0]} (cores: {cpu_count})",
                            "threshold": cpu_count,
                        }
                    )

                return {"success": True, "metrics": metrics, "alerts": alerts}

            except Exception as e:
                return {
                    "success": False,
                    "error": f"Error collecting CPU metrics: {str(e)}",
                }

        # Test normal CPU usage
        result = collect_cpu_metrics()

        assert result["success"] is True
        assert "metrics" in result

        metrics = result["metrics"]
        assert "cpu_percent" in metrics
        assert "cpu_count" in metrics
        assert "load_average" in metrics
        assert "per_core_usage" in metrics
        assert metrics["status"] == "normal"
        assert len(result["alerts"]) == 0

        # Verify data types and ranges
        assert isinstance(metrics["cpu_percent"], (int, float))
        assert 0 <= metrics["cpu_percent"] <= 100
        assert isinstance(metrics["cpu_count"], int)
        assert metrics["cpu_count"] > 0
        assert len(metrics["per_core_usage"]) == metrics["cpu_count"]

    def test_collect_memory_metrics(self):
        """Test memory metrics collection."""

        def collect_memory_metrics():
            """
            Collect memory usage metrics
            """
            try:
                # Mock memory data (in bytes)
                total_memory = 16 * 1024 * 1024 * 1024  # 16 GB
                available_memory = 8 * 1024 * 1024 * 1024  # 8 GB available
                used_memory = total_memory - available_memory
                memory_percent = (used_memory / total_memory) * 100

                # Swap memory
                total_swap = 4 * 1024 * 1024 * 1024  # 4 GB swap
                used_swap = 1024 * 1024 * 1024  # 1 GB used
                swap_percent = (used_swap / total_swap) * 100

                # Buffer and cache
                buffers = 512 * 1024 * 1024  # 512 MB
                cached = 2 * 1024 * 1024 * 1024  # 2 GB

                def bytes_to_gb(bytes_val):
                    return round(bytes_val / (1024 * 1024 * 1024), 2)

                metrics = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "memory": {
                        "total_gb": bytes_to_gb(total_memory),
                        "used_gb": bytes_to_gb(used_memory),
                        "available_gb": bytes_to_gb(available_memory),
                        "percent_used": round(memory_percent, 1),
                        "buffers_gb": bytes_to_gb(buffers),
                        "cached_gb": bytes_to_gb(cached),
                    },
                    "swap": {
                        "total_gb": bytes_to_gb(total_swap),
                        "used_gb": bytes_to_gb(used_swap),
                        "free_gb": bytes_to_gb(total_swap - used_swap),
                        "percent_used": round(swap_percent, 1),
                    },
                    "status": "normal"
                    if memory_percent < 80
                    else "warning"
                    if memory_percent < 90
                    else "critical",
                }

                # Add alerts
                alerts = []
                if memory_percent > 90:
                    alerts.append(
                        {
                            "level": "critical",
                            "message": f"Memory usage is critically high: {memory_percent:.1f}%",
                            "threshold": 90,
                        }
                    )
                elif memory_percent > 80:
                    alerts.append(
                        {
                            "level": "warning",
                            "message": f"Memory usage is high: {memory_percent:.1f}%",
                            "threshold": 80,
                        }
                    )

                if swap_percent > 50:
                    alerts.append(
                        {
                            "level": "warning",
                            "message": f"Swap usage is high: {swap_percent:.1f}%",
                            "threshold": 50,
                        }
                    )

                return {"success": True, "metrics": metrics, "alerts": alerts}

            except Exception as e:
                return {
                    "success": False,
                    "error": f"Error collecting memory metrics: {str(e)}",
                }

        # Test memory metrics collection
        result = collect_memory_metrics()

        assert result["success"] is True
        assert "metrics" in result

        metrics = result["metrics"]
        assert "memory" in metrics
        assert "swap" in metrics

        # Check memory metrics
        memory = metrics["memory"]
        assert memory["total_gb"] > 0
        assert memory["used_gb"] >= 0
        assert memory["available_gb"] >= 0
        assert 0 <= memory["percent_used"] <= 100
        assert memory["total_gb"] == memory["used_gb"] + memory["available_gb"]

        # Check swap metrics
        swap = metrics["swap"]
        assert swap["total_gb"] >= 0
        assert swap["used_gb"] >= 0
        assert swap["free_gb"] >= 0
        assert 0 <= swap["percent_used"] <= 100

        # Check status
        assert metrics["status"] in ["normal", "warning", "critical"]

    def test_collect_disk_metrics(self):
        """Test disk metrics collection."""

        def collect_disk_metrics():
            """
            Collect disk usage metrics for all mounted filesystems
            """
            try:
                # Mock disk data for multiple filesystems
                filesystems = [
                    {
                        "device": "/dev/sda1",
                        "mountpoint": "/",
                        "fstype": "ext4",
                        "total": 100 * 1024 * 1024 * 1024,  # 100 GB
                        "used": 60 * 1024 * 1024 * 1024,  # 60 GB
                        "free": 40 * 1024 * 1024 * 1024,  # 40 GB
                    },
                    {
                        "device": "/dev/sda2",
                        "mountpoint": "/var",
                        "fstype": "ext4",
                        "total": 50 * 1024 * 1024 * 1024,  # 50 GB
                        "used": 45 * 1024 * 1024 * 1024,  # 45 GB
                        "free": 5 * 1024 * 1024 * 1024,  # 5 GB
                    },
                ]

                def bytes_to_gb(bytes_val):
                    return round(bytes_val / (1024 * 1024 * 1024), 2)

                disk_metrics = []
                alerts = []
                overall_status = "normal"

                for fs in filesystems:
                    percent_used = (fs["used"] / fs["total"]) * 100

                    disk_metric = {
                        "device": fs["device"],
                        "mountpoint": fs["mountpoint"],
                        "filesystem": fs["fstype"],
                        "total_gb": bytes_to_gb(fs["total"]),
                        "used_gb": bytes_to_gb(fs["used"]),
                        "free_gb": bytes_to_gb(fs["free"]),
                        "percent_used": round(percent_used, 1),
                        "status": "normal"
                        if percent_used < 80
                        else "warning"
                        if percent_used < 90
                        else "critical",
                    }

                    disk_metrics.append(disk_metric)

                    # Check for alerts
                    if percent_used > 90:
                        alerts.append(
                            {
                                "level": "critical",
                                "message": f"Disk {fs['mountpoint']} is critically full: {percent_used:.1f}%",
                                "device": fs["device"],
                                "mountpoint": fs["mountpoint"],
                                "threshold": 90,
                            }
                        )
                        overall_status = "critical"
                    elif percent_used > 80:
                        alerts.append(
                            {
                                "level": "warning",
                                "message": f"Disk {fs['mountpoint']} is getting full: {percent_used:.1f}%",
                                "device": fs["device"],
                                "mountpoint": fs["mountpoint"],
                                "threshold": 80,
                            }
                        )
                        if overall_status == "normal":
                            overall_status = "warning"

                # Calculate total disk usage
                total_space = sum(fs["total"] for fs in filesystems)
                total_used = sum(fs["used"] for fs in filesystems)
                total_free = sum(fs["free"] for fs in filesystems)
                total_percent = (
                    (total_used / total_space) * 100 if total_space > 0 else 0
                )

                metrics = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "filesystems": disk_metrics,
                    "total": {
                        "total_gb": bytes_to_gb(total_space),
                        "used_gb": bytes_to_gb(total_used),
                        "free_gb": bytes_to_gb(total_free),
                        "percent_used": round(total_percent, 1),
                    },
                    "status": overall_status,
                }

                return {"success": True, "metrics": metrics, "alerts": alerts}

            except Exception as e:
                return {
                    "success": False,
                    "error": f"Error collecting disk metrics: {str(e)}",
                }

        # Test disk metrics collection
        result = collect_disk_metrics()

        assert result["success"] is True
        assert "metrics" in result

        metrics = result["metrics"]
        assert "filesystems" in metrics
        assert "total" in metrics

        # Check filesystem metrics
        filesystems = metrics["filesystems"]
        assert len(filesystems) >= 1

        for fs in filesystems:
            assert "device" in fs
            assert "mountpoint" in fs
            assert "total_gb" in fs
            assert "used_gb" in fs
            assert "free_gb" in fs
            assert "percent_used" in fs
            assert fs["total_gb"] > 0
            assert fs["used_gb"] >= 0
            assert fs["free_gb"] >= 0
            assert 0 <= fs["percent_used"] <= 100

        # Check total metrics
        total = metrics["total"]
        assert total["total_gb"] > 0
        assert total["used_gb"] >= 0
        assert total["free_gb"] >= 0
        assert 0 <= total["percent_used"] <= 100

        # Check for high disk usage alert
        high_usage_fs = next(
            (fs for fs in filesystems if fs["percent_used"] > 80), None
        )
        if high_usage_fs:
            assert len(result["alerts"]) > 0
            assert any("full" in alert["message"].lower() for alert in result["alerts"])


@pytest.mark.asyncio
class TestNetworkMonitoring:
    """Test network monitoring functionality."""

    def test_collect_network_metrics(self):
        """Test network interface metrics collection."""

        def collect_network_metrics():
            """
            Collect network interface metrics
            """
            try:
                # Mock network interface data
                interfaces = {
                    "eth0": {
                        "bytes_sent": 1024 * 1024 * 1024,  # 1 GB
                        "bytes_recv": 2 * 1024 * 1024 * 1024,  # 2 GB
                        "packets_sent": 1000000,
                        "packets_recv": 1500000,
                        "errin": 0,
                        "errout": 0,
                        "dropin": 5,
                        "dropout": 2,
                        "is_up": True,
                        "speed": 1000,  # Mbps
                        "duplex": "full",
                    },
                    "lo": {
                        "bytes_sent": 100 * 1024 * 1024,  # 100 MB
                        "bytes_recv": 100 * 1024 * 1024,  # 100 MB
                        "packets_sent": 50000,
                        "packets_recv": 50000,
                        "errin": 0,
                        "errout": 0,
                        "dropin": 0,
                        "dropout": 0,
                        "is_up": True,
                        "speed": None,  # Loopback has no speed
                        "duplex": None,
                    },
                }

                def bytes_to_mb(bytes_val):
                    return round(bytes_val / (1024 * 1024), 2)

                network_metrics = []
                alerts = []

                for interface, stats in interfaces.items():
                    # Calculate error rates
                    total_packets_sent = stats["packets_sent"]
                    total_packets_recv = stats["packets_recv"]

                    error_rate_out = (
                        (stats["errout"] / total_packets_sent * 100)
                        if total_packets_sent > 0
                        else 0
                    )
                    error_rate_in = (
                        (stats["errin"] / total_packets_recv * 100)
                        if total_packets_recv > 0
                        else 0
                    )
                    drop_rate_out = (
                        (stats["dropout"] / total_packets_sent * 100)
                        if total_packets_sent > 0
                        else 0
                    )
                    drop_rate_in = (
                        (stats["dropin"] / total_packets_recv * 100)
                        if total_packets_recv > 0
                        else 0
                    )

                    interface_metric = {
                        "interface": interface,
                        "is_up": stats["is_up"],
                        "speed_mbps": stats["speed"],
                        "duplex": stats["duplex"],
                        "traffic": {
                            "bytes_sent_mb": bytes_to_mb(stats["bytes_sent"]),
                            "bytes_recv_mb": bytes_to_mb(stats["bytes_recv"]),
                            "packets_sent": stats["packets_sent"],
                            "packets_recv": stats["packets_recv"],
                        },
                        "errors": {
                            "errors_in": stats["errin"],
                            "errors_out": stats["errout"],
                            "drops_in": stats["dropin"],
                            "drops_out": stats["dropout"],
                            "error_rate_in_percent": round(error_rate_in, 4),
                            "error_rate_out_percent": round(error_rate_out, 4),
                            "drop_rate_in_percent": round(drop_rate_in, 4),
                            "drop_rate_out_percent": round(drop_rate_out, 4),
                        },
                    }

                    network_metrics.append(interface_metric)

                    # Check for alerts
                    if not stats["is_up"] and interface != "lo":
                        alerts.append(
                            {
                                "level": "critical",
                                "message": f"Network interface {interface} is down",
                                "interface": interface,
                            }
                        )

                    if error_rate_in > 1 or error_rate_out > 1:
                        alerts.append(
                            {
                                "level": "warning",
                                "message": f"High error rate on interface {interface}: in={error_rate_in:.2f}%, out={error_rate_out:.2f}%",
                                "interface": interface,
                            }
                        )

                    if drop_rate_in > 0.5 or drop_rate_out > 0.5:
                        alerts.append(
                            {
                                "level": "warning",
                                "message": f"Packet drops detected on interface {interface}: in={drop_rate_in:.2f}%, out={drop_rate_out:.2f}%",
                                "interface": interface,
                            }
                        )

                # Calculate total network traffic
                total_bytes_sent = sum(
                    stats["bytes_sent"] for stats in interfaces.values()
                )
                total_bytes_recv = sum(
                    stats["bytes_recv"] for stats in interfaces.values()
                )
                total_packets_sent = sum(
                    stats["packets_sent"] for stats in interfaces.values()
                )
                total_packets_recv = sum(
                    stats["packets_recv"] for stats in interfaces.values()
                )

                metrics = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "interfaces": network_metrics,
                    "total": {
                        "bytes_sent_mb": bytes_to_mb(total_bytes_sent),
                        "bytes_recv_mb": bytes_to_mb(total_bytes_recv),
                        "packets_sent": total_packets_sent,
                        "packets_recv": total_packets_recv,
                    },
                    "active_interfaces": len(
                        [i for i in network_metrics if i["is_up"]]
                    ),
                    "status": "normal"
                    if len(alerts) == 0
                    else "warning"
                    if all(a["level"] == "warning" for a in alerts)
                    else "critical",
                }

                return {"success": True, "metrics": metrics, "alerts": alerts}

            except Exception as e:
                return {
                    "success": False,
                    "error": f"Error collecting network metrics: {str(e)}",
                }

        # Test network metrics collection
        result = collect_network_metrics()

        assert result["success"] is True
        assert "metrics" in result

        metrics = result["metrics"]
        assert "interfaces" in metrics
        assert "total" in metrics

        # Check interface metrics
        interfaces = metrics["interfaces"]
        assert len(interfaces) >= 1

        for interface in interfaces:
            assert "interface" in interface
            assert "is_up" in interface
            assert "traffic" in interface
            assert "errors" in interface

            traffic = interface["traffic"]
            assert traffic["bytes_sent_mb"] >= 0
            assert traffic["bytes_recv_mb"] >= 0
            assert traffic["packets_sent"] >= 0
            assert traffic["packets_recv"] >= 0

            errors = interface["errors"]
            assert errors["errors_in"] >= 0
            assert errors["errors_out"] >= 0
            assert errors["drops_in"] >= 0
            assert errors["drops_out"] >= 0

        # Check total metrics
        total = metrics["total"]
        assert total["bytes_sent_mb"] >= 0
        assert total["bytes_recv_mb"] >= 0
        assert total["packets_sent"] >= 0
        assert total["packets_recv"] >= 0

        # Check active interfaces count
        assert metrics["active_interfaces"] >= 0
        assert metrics["active_interfaces"] <= len(interfaces)

    def test_check_network_connectivity(self):
        """Test network connectivity checks."""

        def check_network_connectivity(hosts=None):
            """
            Check network connectivity to external hosts
            """
            try:
                if hosts is None:
                    hosts = [
                        {"host": "8.8.8.8", "name": "Google DNS", "timeout": 5},
                        {"host": "1.1.1.1", "name": "Cloudflare DNS", "timeout": 5},
                        {"host": "google.com", "name": "Google", "timeout": 10},
                        {"host": "github.com", "name": "GitHub", "timeout": 10},
                    ]

                connectivity_results = []
                successful_checks = 0

                for host_config in hosts:
                    host = host_config["host"]
                    name = host_config["name"]
                    timeout = host_config["timeout"]

                    # Mock ping/connectivity check
                    # In real implementation, this would use subprocess.run(['ping', ...])
                    # or socket connection test

                    # Simulate different connectivity scenarios
                    if host in ["8.8.8.8", "google.com"]:
                        # Simulate successful connection
                        is_reachable = True
                        response_time = 15.2  # ms
                        error = None
                    elif host == "1.1.1.1":
                        # Simulate successful but slower connection
                        is_reachable = True
                        response_time = 45.8  # ms
                        error = None
                    else:
                        # Simulate failed connection
                        is_reachable = False
                        response_time = None
                        error = "Request timeout"

                    result = {
                        "host": host,
                        "name": name,
                        "is_reachable": is_reachable,
                        "response_time_ms": response_time,
                        "error": error,
                        "timestamp": datetime.utcnow().isoformat(),
                    }

                    connectivity_results.append(result)

                    if is_reachable:
                        successful_checks += 1

                # Calculate connectivity status
                success_rate = (successful_checks / len(hosts)) * 100

                if success_rate == 100:
                    status = "excellent"
                elif success_rate >= 75:
                    status = "good"
                elif success_rate >= 50:
                    status = "poor"
                else:
                    status = "critical"

                # Generate alerts
                alerts = []
                failed_hosts = [
                    r for r in connectivity_results if not r["is_reachable"]
                ]

                if len(failed_hosts) > 0:
                    if len(failed_hosts) == len(hosts):
                        alerts.append(
                            {
                                "level": "critical",
                                "message": "All connectivity checks failed - possible network outage",
                                "failed_hosts": [h["name"] for h in failed_hosts],
                            }
                        )
                    else:
                        alerts.append(
                            {
                                "level": "warning",
                                "message": f"Some connectivity checks failed: {', '.join(h['name'] for h in failed_hosts)}",
                                "failed_hosts": [h["name"] for h in failed_hosts],
                            }
                        )

                # Check for slow responses
                slow_hosts = [
                    r
                    for r in connectivity_results
                    if r["is_reachable"]
                    and r["response_time_ms"]
                    and r["response_time_ms"] > 100
                ]
                if slow_hosts:
                    alerts.append(
                        {
                            "level": "warning",
                            "message": f"Slow network responses detected: {', '.join(h['name'] for h in slow_hosts)}",
                            "slow_hosts": [h["name"] for h in slow_hosts],
                        }
                    )

                metrics = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "connectivity_checks": connectivity_results,
                    "summary": {
                        "total_checks": len(hosts),
                        "successful_checks": successful_checks,
                        "failed_checks": len(hosts) - successful_checks,
                        "success_rate_percent": round(success_rate, 1),
                        "average_response_time_ms": round(
                            sum(
                                r["response_time_ms"]
                                for r in connectivity_results
                                if r["response_time_ms"]
                            )
                            / len(
                                [
                                    r
                                    for r in connectivity_results
                                    if r["response_time_ms"]
                                ]
                            ),
                            1,
                        )
                        if any(r["response_time_ms"] for r in connectivity_results)
                        else None,
                    },
                    "status": status,
                }

                return {"success": True, "metrics": metrics, "alerts": alerts}

            except Exception as e:
                return {
                    "success": False,
                    "error": f"Error checking network connectivity: {str(e)}",
                }

        # Test network connectivity check
        result = check_network_connectivity()

        assert result["success"] is True
        assert "metrics" in result

        metrics = result["metrics"]
        assert "connectivity_checks" in metrics
        assert "summary" in metrics

        # Check connectivity results
        checks = metrics["connectivity_checks"]
        assert len(checks) >= 1

        for check in checks:
            assert "host" in check
            assert "name" in check
            assert "is_reachable" in check
            assert isinstance(check["is_reachable"], bool)

            if check["is_reachable"]:
                assert check["response_time_ms"] is not None
                assert check["response_time_ms"] > 0
            else:
                assert check["error"] is not None

        # Check summary
        summary = metrics["summary"]
        assert summary["total_checks"] == len(checks)
        assert summary["successful_checks"] >= 0
        assert summary["failed_checks"] >= 0
        assert (
            summary["successful_checks"] + summary["failed_checks"]
            == summary["total_checks"]
        )
        assert 0 <= summary["success_rate_percent"] <= 100

        # Check status
        assert metrics["status"] in ["excellent", "good", "poor", "critical"]


@pytest.mark.asyncio
class TestServiceHealthChecks:
    """Test service health check functionality."""

    def test_check_database_health(self):
        """Test database health checks."""

        def check_database_health(databases=None):
            """
            Check health of database connections
            """
            try:
                if databases is None:
                    databases = [
                        {"name": "user_service_db", "host": "localhost", "port": 5432},
                        {
                            "name": "payment_service_db",
                            "host": "localhost",
                            "port": 5432,
                        },
                        {"name": "math_solver_db", "host": "localhost", "port": 5432},
                        {
                            "name": "content_service_db",
                            "host": "localhost",
                            "port": 5432,
                        },
                        {"name": "admin_service_db", "host": "localhost", "port": 5432},
                    ]

                health_results = []
                healthy_databases = 0

                for db_config in databases:
                    db_name = db_config["name"]
                    host = db_config["host"]
                    port = db_config["port"]

                    # Mock database connection check
                    # In real implementation, this would attempt actual database connection

                    # Simulate different database states
                    if "user_service" in db_name or "payment_service" in db_name:
                        # Simulate healthy databases
                        is_healthy = True
                        response_time = 12.5  # ms
                        error = None
                        connection_count = 5
                        max_connections = 100
                    elif "math_solver" in db_name:
                        # Simulate slow but healthy database
                        is_healthy = True
                        response_time = 85.2  # ms
                        error = None
                        connection_count = 15
                        max_connections = 100
                    else:
                        # Simulate unhealthy database
                        is_healthy = False
                        response_time = None
                        error = "Connection timeout"
                        connection_count = None
                        max_connections = None

                    result = {
                        "database": db_name,
                        "host": host,
                        "port": port,
                        "is_healthy": is_healthy,
                        "response_time_ms": response_time,
                        "error": error,
                        "connection_info": {
                            "active_connections": connection_count,
                            "max_connections": max_connections,
                            "connection_usage_percent": round(
                                (connection_count / max_connections) * 100, 1
                            )
                            if connection_count and max_connections
                            else None,
                        },
                        "timestamp": datetime.utcnow().isoformat(),
                    }

                    health_results.append(result)

                    if is_healthy:
                        healthy_databases += 1

                # Calculate overall health
                health_rate = (healthy_databases / len(databases)) * 100

                if health_rate == 100:
                    overall_status = "healthy"
                elif health_rate >= 80:
                    overall_status = "degraded"
                else:
                    overall_status = "unhealthy"

                # Generate alerts
                alerts = []
                unhealthy_dbs = [r for r in health_results if not r["is_healthy"]]

                for db in unhealthy_dbs:
                    alerts.append(
                        {
                            "level": "critical",
                            "message": f"Database {db['database']} is unhealthy: {db['error']}",
                            "database": db["database"],
                            "error": db["error"],
                        }
                    )

                # Check for slow databases
                slow_dbs = [
                    r
                    for r in health_results
                    if r["is_healthy"]
                    and r["response_time_ms"]
                    and r["response_time_ms"] > 50
                ]
                for db in slow_dbs:
                    alerts.append(
                        {
                            "level": "warning",
                            "message": f"Database {db['database']} is responding slowly: {db['response_time_ms']}ms",
                            "database": db["database"],
                            "response_time": db["response_time_ms"],
                        }
                    )

                # Check for high connection usage
                high_usage_dbs = [
                    r
                    for r in health_results
                    if r["is_healthy"]
                    and r["connection_info"]["connection_usage_percent"]
                    and r["connection_info"]["connection_usage_percent"] > 80
                ]
                for db in high_usage_dbs:
                    alerts.append(
                        {
                            "level": "warning",
                            "message": f"Database {db['database']} has high connection usage: {db['connection_info']['connection_usage_percent']}%",
                            "database": db["database"],
                            "usage_percent": db["connection_info"][
                                "connection_usage_percent"
                            ],
                        }
                    )

                metrics = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "database_checks": health_results,
                    "summary": {
                        "total_databases": len(databases),
                        "healthy_databases": healthy_databases,
                        "unhealthy_databases": len(databases) - healthy_databases,
                        "health_rate_percent": round(health_rate, 1),
                        "average_response_time_ms": round(
                            sum(
                                r["response_time_ms"]
                                for r in health_results
                                if r["response_time_ms"]
                            )
                            / len([r for r in health_results if r["response_time_ms"]]),
                            1,
                        )
                        if any(r["response_time_ms"] for r in health_results)
                        else None,
                    },
                    "status": overall_status,
                }

                return {"success": True, "metrics": metrics, "alerts": alerts}

            except Exception as e:
                return {
                    "success": False,
                    "error": f"Error checking database health: {str(e)}",
                }

        # Test database health check
        result = check_database_health()

        assert result["success"] is True
        assert "metrics" in result

        metrics = result["metrics"]
        assert "database_checks" in metrics
        assert "summary" in metrics

        # Check database results
        checks = metrics["database_checks"]
        assert len(checks) == 5  # 5 databases

        for check in checks:
            assert "database" in check
            assert "is_healthy" in check
            assert isinstance(check["is_healthy"], bool)

            if check["is_healthy"]:
                assert check["response_time_ms"] is not None
                assert check["response_time_ms"] > 0
                assert check["connection_info"]["active_connections"] is not None
            else:
                assert check["error"] is not None

        # Check summary
        summary = metrics["summary"]
        assert summary["total_databases"] == 5
        assert summary["healthy_databases"] >= 0
        assert summary["unhealthy_databases"] >= 0
        assert summary["healthy_databases"] + summary["unhealthy_databases"] == 5
        assert 0 <= summary["health_rate_percent"] <= 100

        # Check status
        assert metrics["status"] in ["healthy", "degraded", "unhealthy"]

        # Should have alerts for unhealthy databases
        if summary["unhealthy_databases"] > 0:
            assert len(result["alerts"]) > 0
            assert any(
                "unhealthy" in alert["message"].lower() for alert in result["alerts"]
            )

    def test_check_redis_health(self):
        """Test Redis health checks."""

        def check_redis_health(redis_instances=None):
            """
            Check health of Redis instances
            """
            try:
                if redis_instances is None:
                    redis_instances = [
                        {
                            "name": "user_cache",
                            "host": "localhost",
                            "port": 6379,
                            "db": 0,
                        },
                        {
                            "name": "payment_cache",
                            "host": "localhost",
                            "port": 6379,
                            "db": 1,
                        },
                        {
                            "name": "math_cache",
                            "host": "localhost",
                            "port": 6379,
                            "db": 2,
                        },
                        {
                            "name": "content_cache",
                            "host": "localhost",
                            "port": 6379,
                            "db": 3,
                        },
                        {
                            "name": "admin_cache",
                            "host": "localhost",
                            "port": 6379,
                            "db": 4,
                        },
                    ]

                health_results = []
                healthy_instances = 0

                for redis_config in redis_instances:
                    name = redis_config["name"]
                    host = redis_config["host"]
                    port = redis_config["port"]
                    db = redis_config["db"]

                    # Mock Redis connection check
                    # In real implementation, this would use redis.Redis().ping()

                    # Simulate different Redis states
                    if "user_cache" in name or "payment_cache" in name:
                        # Simulate healthy Redis instances
                        is_healthy = True
                        response_time = 2.1  # ms
                        error = None
                        memory_usage = 45 * 1024 * 1024  # 45 MB
                        connected_clients = 12
                        keys_count = 1500
                    elif "math_cache" in name:
                        # Simulate healthy but high memory usage
                        is_healthy = True
                        response_time = 3.8  # ms
                        error = None
                        memory_usage = 180 * 1024 * 1024  # 180 MB
                        connected_clients = 8
                        keys_count = 5000
                    else:
                        # Simulate unhealthy Redis instance
                        is_healthy = False
                        response_time = None
                        error = "Connection refused"
                        memory_usage = None
                        connected_clients = None
                        keys_count = None

                    def bytes_to_mb(bytes_val):
                        return (
                            round(bytes_val / (1024 * 1024), 2) if bytes_val else None
                        )

                    result = {
                        "instance": name,
                        "host": host,
                        "port": port,
                        "database": db,
                        "is_healthy": is_healthy,
                        "response_time_ms": response_time,
                        "error": error,
                        "stats": {
                            "memory_usage_mb": bytes_to_mb(memory_usage),
                            "connected_clients": connected_clients,
                            "keys_count": keys_count,
                        },
                        "timestamp": datetime.utcnow().isoformat(),
                    }

                    health_results.append(result)

                    if is_healthy:
                        healthy_instances += 1

                # Calculate overall health
                health_rate = (healthy_instances / len(redis_instances)) * 100

                if health_rate == 100:
                    overall_status = "healthy"
                elif health_rate >= 80:
                    overall_status = "degraded"
                else:
                    overall_status = "unhealthy"

                # Generate alerts
                alerts = []
                unhealthy_instances = [r for r in health_results if not r["is_healthy"]]

                for instance in unhealthy_instances:
                    alerts.append(
                        {
                            "level": "critical",
                            "message": f"Redis instance {instance['instance']} is unhealthy: {instance['error']}",
                            "instance": instance["instance"],
                            "error": instance["error"],
                        }
                    )

                # Check for high memory usage
                high_memory_instances = [
                    r
                    for r in health_results
                    if r["is_healthy"]
                    and r["stats"]["memory_usage_mb"]
                    and r["stats"]["memory_usage_mb"] > 150
                ]
                for instance in high_memory_instances:
                    alerts.append(
                        {
                            "level": "warning",
                            "message": f"Redis instance {instance['instance']} has high memory usage: {instance['stats']['memory_usage_mb']}MB",
                            "instance": instance["instance"],
                            "memory_usage": instance["stats"]["memory_usage_mb"],
                        }
                    )

                # Calculate total stats
                total_memory = sum(
                    r["stats"]["memory_usage_mb"]
                    for r in health_results
                    if r["stats"]["memory_usage_mb"]
                )
                total_clients = sum(
                    r["stats"]["connected_clients"]
                    for r in health_results
                    if r["stats"]["connected_clients"]
                )
                total_keys = sum(
                    r["stats"]["keys_count"]
                    for r in health_results
                    if r["stats"]["keys_count"]
                )

                metrics = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "redis_checks": health_results,
                    "summary": {
                        "total_instances": len(redis_instances),
                        "healthy_instances": healthy_instances,
                        "unhealthy_instances": len(redis_instances) - healthy_instances,
                        "health_rate_percent": round(health_rate, 1),
                        "total_memory_usage_mb": round(total_memory, 2),
                        "total_connected_clients": total_clients,
                        "total_keys": total_keys,
                        "average_response_time_ms": round(
                            sum(
                                r["response_time_ms"]
                                for r in health_results
                                if r["response_time_ms"]
                            )
                            / len([r for r in health_results if r["response_time_ms"]]),
                            1,
                        )
                        if any(r["response_time_ms"] for r in health_results)
                        else None,
                    },
                    "status": overall_status,
                }

                return {"success": True, "metrics": metrics, "alerts": alerts}

            except Exception as e:
                return {
                    "success": False,
                    "error": f"Error checking Redis health: {str(e)}",
                }

        # Test Redis health check
        result = check_redis_health()

        assert result["success"] is True
        assert "metrics" in result

        metrics = result["metrics"]
        assert "redis_checks" in metrics
        assert "summary" in metrics

        # Check Redis results
        checks = metrics["redis_checks"]
        assert len(checks) == 5  # 5 Redis instances

        for check in checks:
            assert "instance" in check
            assert "is_healthy" in check
            assert isinstance(check["is_healthy"], bool)

            if check["is_healthy"]:
                assert check["response_time_ms"] is not None
                assert check["response_time_ms"] > 0
                assert check["stats"]["memory_usage_mb"] is not None
                assert check["stats"]["connected_clients"] is not None
                assert check["stats"]["keys_count"] is not None
            else:
                assert check["error"] is not None

        # Check summary
        summary = metrics["summary"]
        assert summary["total_instances"] == 5
        assert summary["healthy_instances"] >= 0
        assert summary["unhealthy_instances"] >= 0
        assert summary["healthy_instances"] + summary["unhealthy_instances"] == 5
        assert 0 <= summary["health_rate_percent"] <= 100

        # Check status
        assert metrics["status"] in ["healthy", "degraded", "unhealthy"]

        # Should have alerts for unhealthy instances
        if summary["unhealthy_instances"] > 0:
            assert len(result["alerts"]) > 0
            assert any(
                "unhealthy" in alert["message"].lower() for alert in result["alerts"]
            )
