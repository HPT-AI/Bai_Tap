"""
Unit tests for Audit Logging functionality.
"""

import hashlib
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Mock imports - these would be actual imports in real implementation
# from admin_service.services import AuditService, SecurityService
# from admin_service.models import AuditLog, SecurityEvent, UserActivity
# from admin_service.schemas import AuditEntry, SecurityAlert


@pytest.mark.asyncio
class TestAuditLogging:
    """Test audit logging functionality."""

    def test_log_user_activity(self, sample_audit_data):
        """Test logging user activities."""

        def log_user_activity(
            user_id,
            action,
            resource_type,
            resource_id=None,
            details=None,
            ip_address=None,
            user_agent=None,
        ):
            """
            Log user activity for audit purposes
            """
            try:
                # Generate unique audit ID
                audit_id = f"audit_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{user_id}_{hash(action) % 10000}"

                # Determine risk level based on action
                high_risk_actions = [
                    "delete_user",
                    "change_password",
                    "grant_admin",
                    "revoke_admin",
                    "delete_payment",
                    "refund_payment",
                    "system_config_change",
                ]
                medium_risk_actions = [
                    "create_user",
                    "update_user",
                    "login",
                    "logout",
                    "create_payment",
                    "update_payment",
                    "publish_content",
                ]

                if action in high_risk_actions:
                    risk_level = "high"
                elif action in medium_risk_actions:
                    risk_level = "medium"
                else:
                    risk_level = "low"

                # Create audit entry
                audit_entry = {
                    "audit_id": audit_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "user_id": user_id,
                    "action": action,
                    "resource_type": resource_type,
                    "resource_id": resource_id,
                    "risk_level": risk_level,
                    "details": details or {},
                    "metadata": {
                        "ip_address": ip_address,
                        "user_agent": user_agent,
                        "session_id": f"session_{user_id}_{hash(str(datetime.utcnow())) % 100000}",
                        "request_id": f"req_{hash(audit_id) % 1000000}",
                    },
                    "status": "success",
                }

                # Add additional context based on action type
                if action == "login":
                    audit_entry["details"].update(
                        {
                            "login_method": details.get("login_method", "password"),
                            "two_factor_used": details.get("two_factor_used", False),
                            "device_fingerprint": details.get("device_fingerprint"),
                        }
                    )
                elif action == "delete_user":
                    audit_entry["details"].update(
                        {
                            "deleted_user_email": details.get("deleted_user_email"),
                            "reason": details.get("reason", "Not specified"),
                            "data_retention_days": details.get(
                                "data_retention_days", 30
                            ),
                        }
                    )
                elif action in ["create_payment", "update_payment", "delete_payment"]:
                    audit_entry["details"].update(
                        {
                            "amount": details.get("amount"),
                            "currency": details.get("currency", "VND"),
                            "payment_method": details.get("payment_method"),
                            "transaction_id": details.get("transaction_id"),
                        }
                    )

                # Generate integrity hash
                hash_data = f"{audit_id}{user_id}{action}{resource_type}{audit_entry['timestamp']}"
                audit_entry["integrity_hash"] = hashlib.sha256(
                    hash_data.encode()
                ).hexdigest()

                # Simulate database storage
                # In real implementation: await audit_repository.create(audit_entry)

                return {
                    "success": True,
                    "audit_id": audit_id,
                    "audit_entry": audit_entry,
                }

            except Exception as e:
                return {
                    "success": False,
                    "error": f"Error logging audit entry: {str(e)}",
                }

        # Test user login audit
        result = log_user_activity(
            user_id=123,
            action="login",
            resource_type="user",
            resource_id=123,
            details={
                "login_method": "password",
                "two_factor_used": True,
                "device_fingerprint": "fp_abc123",
            },
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        )

        assert result["success"] is True
        assert "audit_id" in result
        assert "audit_entry" in result

        audit_entry = result["audit_entry"]

        # Check basic fields
        assert audit_entry["user_id"] == 123
        assert audit_entry["action"] == "login"
        assert audit_entry["resource_type"] == "user"
        assert audit_entry["resource_id"] == 123
        assert audit_entry["risk_level"] == "medium"
        assert audit_entry["status"] == "success"

        # Check metadata
        assert audit_entry["metadata"]["ip_address"] == "192.168.1.100"
        assert "Mozilla" in audit_entry["metadata"]["user_agent"]
        assert audit_entry["metadata"]["session_id"].startswith("session_")
        assert audit_entry["metadata"]["request_id"].startswith("req_")

        # Check login-specific details
        assert audit_entry["details"]["login_method"] == "password"
        assert audit_entry["details"]["two_factor_used"] is True
        assert audit_entry["details"]["device_fingerprint"] == "fp_abc123"

        # Check integrity hash
        assert "integrity_hash" in audit_entry
        assert len(audit_entry["integrity_hash"]) == 64  # SHA256 hex length

        # Test high-risk action audit
        result = log_user_activity(
            user_id=456,
            action="delete_user",
            resource_type="user",
            resource_id=789,
            details={
                "deleted_user_email": "user@example.com",
                "reason": "Account violation",
                "data_retention_days": 90,
            },
            ip_address="10.0.0.5",
        )

        assert result["success"] is True
        audit_entry = result["audit_entry"]

        # Should be high risk
        assert audit_entry["risk_level"] == "high"
        assert audit_entry["details"]["deleted_user_email"] == "user@example.com"
        assert audit_entry["details"]["reason"] == "Account violation"
        assert audit_entry["details"]["data_retention_days"] == 90

    def test_log_system_events(self):
        """Test logging system events."""

        def log_system_event(
            event_type, severity, message, component=None, details=None
        ):
            """
            Log system events for monitoring and debugging
            """
            try:
                # Generate unique event ID
                event_id = f"event_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{hash(message) % 10000}"

                # Validate severity level
                valid_severities = ["debug", "info", "warning", "error", "critical"]
                if severity not in valid_severities:
                    severity = "info"

                # Create system event entry
                event_entry = {
                    "event_id": event_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "event_type": event_type,
                    "severity": severity,
                    "message": message,
                    "component": component or "system",
                    "details": details or {},
                    "metadata": {
                        "hostname": "math-service-server",
                        "process_id": 12345,
                        "thread_id": 67890,
                        "environment": "production",
                    },
                }

                # Add component-specific details
                if component == "database":
                    event_entry["details"].update(
                        {
                            "database_name": details.get("database_name"),
                            "query_duration_ms": details.get("query_duration_ms"),
                            "affected_rows": details.get("affected_rows"),
                            "connection_pool_size": details.get(
                                "connection_pool_size", 10
                            ),
                        }
                    )
                elif component == "payment_gateway":
                    event_entry["details"].update(
                        {
                            "gateway_name": details.get("gateway_name"),
                            "transaction_id": details.get("transaction_id"),
                            "response_code": details.get("response_code"),
                            "response_time_ms": details.get("response_time_ms"),
                        }
                    )
                elif component == "cache":
                    event_entry["details"].update(
                        {
                            "cache_type": details.get("cache_type", "redis"),
                            "cache_key": details.get("cache_key"),
                            "hit_rate_percent": details.get("hit_rate_percent"),
                            "memory_usage_mb": details.get("memory_usage_mb"),
                        }
                    )

                # Add alert flag for critical events
                if severity in ["error", "critical"]:
                    event_entry["requires_alert"] = True
                    event_entry["alert_channels"] = ["email", "slack"]

                    if severity == "critical":
                        event_entry["alert_channels"].append("sms")
                else:
                    event_entry["requires_alert"] = False

                # Generate event hash for deduplication
                hash_data = f"{event_type}{component}{message}"
                event_entry["event_hash"] = hashlib.md5(hash_data.encode()).hexdigest()

                return {
                    "success": True,
                    "event_id": event_id,
                    "event_entry": event_entry,
                }

            except Exception as e:
                return {
                    "success": False,
                    "error": f"Error logging system event: {str(e)}",
                }

        # Test database error event
        result = log_system_event(
            event_type="database_error",
            severity="error",
            message="Database connection timeout",
            component="database",
            details={
                "database_name": "user_service_db",
                "query_duration_ms": 30000,
                "connection_pool_size": 10,
                "error_code": "CONNECTION_TIMEOUT",
            },
        )

        assert result["success"] is True
        assert "event_id" in result

        event_entry = result["event_entry"]

        # Check basic fields
        assert event_entry["event_type"] == "database_error"
        assert event_entry["severity"] == "error"
        assert event_entry["component"] == "database"
        assert event_entry["requires_alert"] is True
        assert "email" in event_entry["alert_channels"]
        assert "slack" in event_entry["alert_channels"]

        # Check database-specific details
        assert event_entry["details"]["database_name"] == "user_service_db"
        assert event_entry["details"]["query_duration_ms"] == 30000
        assert event_entry["details"]["connection_pool_size"] == 10

        # Check metadata
        assert event_entry["metadata"]["hostname"] == "math-service-server"
        assert event_entry["metadata"]["environment"] == "production"

        # Test critical system event
        result = log_system_event(
            event_type="system_failure",
            severity="critical",
            message="Payment gateway completely unavailable",
            component="payment_gateway",
            details={
                "gateway_name": "VNPay",
                "response_code": 500,
                "consecutive_failures": 10,
            },
        )

        assert result["success"] is True
        event_entry = result["event_entry"]

        # Critical events should have SMS alerts
        assert event_entry["severity"] == "critical"
        assert event_entry["requires_alert"] is True
        assert "sms" in event_entry["alert_channels"]

        # Test info level event (no alerts)
        result = log_system_event(
            event_type="cache_hit",
            severity="info",
            message="Cache hit rate improved",
            component="cache",
            details={
                "cache_type": "redis",
                "hit_rate_percent": 95.2,
                "memory_usage_mb": 128,
            },
        )

        assert result["success"] is True
        event_entry = result["event_entry"]

        # Info events should not require alerts
        assert event_entry["severity"] == "info"
        assert event_entry["requires_alert"] is False


@pytest.mark.asyncio
class TestSecurityAuditing:
    """Test security-specific auditing functionality."""

    def test_log_security_events(self):
        """Test logging security-related events."""

        def log_security_event(
            event_type, user_id=None, ip_address=None, severity="medium", details=None
        ):
            """
            Log security events for threat detection and compliance
            """
            try:
                # Generate unique security event ID
                security_id = f"sec_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{hash(event_type) % 10000}"

                # Define security event categories
                authentication_events = [
                    "failed_login",
                    "successful_login",
                    "password_change",
                    "account_locked",
                ]
                authorization_events = [
                    "unauthorized_access",
                    "privilege_escalation",
                    "permission_denied",
                ]
                data_events = ["data_export", "data_deletion", "sensitive_data_access"]
                system_events = [
                    "suspicious_activity",
                    "malware_detected",
                    "intrusion_attempt",
                ]

                # Determine event category
                if event_type in authentication_events:
                    category = "authentication"
                elif event_type in authorization_events:
                    category = "authorization"
                elif event_type in data_events:
                    category = "data_access"
                elif event_type in system_events:
                    category = "system_security"
                else:
                    category = "general"

                # Create security event entry
                security_entry = {
                    "security_id": security_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "event_type": event_type,
                    "category": category,
                    "severity": severity,
                    "user_id": user_id,
                    "ip_address": ip_address,
                    "details": details or {},
                    "metadata": {
                        "detection_method": "automated",
                        "confidence_score": 0.85,
                        "false_positive_probability": 0.15,
                        "investigation_required": severity in ["high", "critical"],
                    },
                }

                # Add event-specific details
                if event_type == "failed_login":
                    security_entry["details"].update(
                        {
                            "failure_reason": details.get(
                                "failure_reason", "invalid_credentials"
                            ),
                            "attempt_count": details.get("attempt_count", 1),
                            "user_agent": details.get("user_agent"),
                            "geolocation": details.get("geolocation"),
                        }
                    )

                    # Escalate severity for multiple failures
                    attempt_count = details.get("attempt_count", 1)
                    if attempt_count >= 5:
                        security_entry["severity"] = "high"
                        security_entry["metadata"]["investigation_required"] = True

                elif event_type == "unauthorized_access":
                    security_entry["details"].update(
                        {
                            "requested_resource": details.get("requested_resource"),
                            "required_permission": details.get("required_permission"),
                            "user_permissions": details.get("user_permissions", []),
                            "access_method": details.get("access_method", "web"),
                        }
                    )

                elif event_type == "suspicious_activity":
                    security_entry["details"].update(
                        {
                            "activity_type": details.get("activity_type"),
                            "anomaly_score": details.get("anomaly_score", 0.5),
                            "baseline_behavior": details.get("baseline_behavior"),
                            "detected_patterns": details.get("detected_patterns", []),
                        }
                    )

                    # High anomaly scores require investigation
                    anomaly_score = details.get("anomaly_score", 0.5)
                    if anomaly_score > 0.8:
                        security_entry["severity"] = "high"
                        security_entry["metadata"]["investigation_required"] = True

                # Add threat intelligence context
                if ip_address:
                    # Mock threat intelligence lookup
                    threat_intel = {
                        "is_known_threat": ip_address
                        in ["192.168.1.666", "10.0.0.999"],  # Mock malicious IPs
                        "reputation_score": 0.2
                        if ip_address.startswith("192.168.1")
                        else 0.8,
                        "country": "VN"
                        if ip_address.startswith("192.168")
                        else "Unknown",
                        "isp": "Local ISP"
                        if ip_address.startswith("192.168")
                        else "Unknown",
                    }
                    security_entry["threat_intelligence"] = threat_intel

                    # Escalate if known threat
                    if threat_intel["is_known_threat"]:
                        security_entry["severity"] = "critical"
                        security_entry["metadata"]["investigation_required"] = True

                # Add compliance tags
                compliance_tags = []
                if category == "authentication":
                    compliance_tags.extend(["PCI-DSS", "SOX"])
                if category == "data_access":
                    compliance_tags.extend(["GDPR", "PCI-DSS"])
                if event_type in ["data_export", "data_deletion"]:
                    compliance_tags.append("Data-Retention-Policy")

                security_entry["compliance_tags"] = compliance_tags

                # Generate security hash
                hash_data = f"{security_id}{event_type}{user_id}{ip_address}{security_entry['timestamp']}"
                security_entry["security_hash"] = hashlib.sha256(
                    hash_data.encode()
                ).hexdigest()

                return {
                    "success": True,
                    "security_id": security_id,
                    "security_entry": security_entry,
                }

            except Exception as e:
                return {
                    "success": False,
                    "error": f"Error logging security event: {str(e)}",
                }

        # Test failed login security event
        result = log_security_event(
            event_type="failed_login",
            user_id=123,
            ip_address="192.168.1.100",
            severity="medium",
            details={
                "failure_reason": "invalid_password",
                "attempt_count": 3,
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "geolocation": {"country": "VN", "city": "Ho Chi Minh City"},
            },
        )

        assert result["success"] is True
        assert "security_id" in result

        security_entry = result["security_entry"]

        # Check basic fields
        assert security_entry["event_type"] == "failed_login"
        assert security_entry["category"] == "authentication"
        assert security_entry["user_id"] == 123
        assert security_entry["ip_address"] == "192.168.1.100"

        # Check failed login details
        assert security_entry["details"]["failure_reason"] == "invalid_password"
        assert security_entry["details"]["attempt_count"] == 3

        # Check compliance tags
        assert "PCI-DSS" in security_entry["compliance_tags"]
        assert "SOX" in security_entry["compliance_tags"]

        # Check threat intelligence
        assert "threat_intelligence" in security_entry
        assert security_entry["threat_intelligence"]["country"] == "VN"

        # Test high-severity security event
        result = log_security_event(
            event_type="failed_login",
            user_id=456,
            ip_address="192.168.1.666",  # Mock malicious IP
            severity="medium",
            details={
                "failure_reason": "account_not_found",
                "attempt_count": 10,  # High attempt count
            },
        )

        assert result["success"] is True
        security_entry = result["security_entry"]

        # Should escalate severity due to high attempt count and malicious IP
        assert (
            security_entry["severity"] == "critical"
        )  # Escalated due to known threat IP
        assert security_entry["metadata"]["investigation_required"] is True
        assert security_entry["threat_intelligence"]["is_known_threat"] is True

        # Test unauthorized access event
        result = log_security_event(
            event_type="unauthorized_access",
            user_id=789,
            ip_address="10.0.0.50",
            severity="high",
            details={
                "requested_resource": "/admin/users",
                "required_permission": "admin:users:read",
                "user_permissions": ["user:profile:read", "user:profile:update"],
                "access_method": "api",
            },
        )

        assert result["success"] is True
        security_entry = result["security_entry"]

        # Check authorization event details
        assert security_entry["category"] == "authorization"
        assert security_entry["details"]["requested_resource"] == "/admin/users"
        assert security_entry["details"]["required_permission"] == "admin:users:read"
        assert "user:profile:read" in security_entry["details"]["user_permissions"]

    def test_audit_trail_integrity(self):
        """Test audit trail integrity verification."""

        def verify_audit_integrity(audit_entries):
            """
            Verify the integrity of audit trail entries
            """
            try:
                verification_results = []
                total_entries = len(audit_entries)
                valid_entries = 0

                for entry in audit_entries:
                    entry_id = (
                        entry.get("audit_id")
                        or entry.get("security_id")
                        or entry.get("event_id")
                    )

                    # Verify required fields
                    required_fields = ["timestamp", "user_id"]
                    missing_fields = [
                        field
                        for field in required_fields
                        if field not in entry or entry[field] is None
                    ]

                    # Verify integrity hash if present
                    hash_valid = True
                    if "integrity_hash" in entry:
                        # Reconstruct hash data
                        if "audit_id" in entry:
                            hash_data = f"{entry['audit_id']}{entry.get('user_id')}{entry.get('action')}{entry.get('resource_type')}{entry['timestamp']}"
                        elif "security_hash" in entry:
                            hash_data = f"{entry.get('security_id')}{entry.get('event_type')}{entry.get('user_id')}{entry.get('ip_address')}{entry['timestamp']}"
                        else:
                            hash_data = f"{entry_id}{entry['timestamp']}"

                        expected_hash = hashlib.sha256(hash_data.encode()).hexdigest()
                        hash_valid = (
                            entry.get("integrity_hash") == expected_hash
                            or entry.get("security_hash") == expected_hash
                        )

                    # Verify timestamp format and validity
                    timestamp_valid = True
                    try:
                        timestamp = datetime.fromisoformat(
                            entry["timestamp"].replace("Z", "+00:00")
                        )
                        # Check if timestamp is not in the future
                        if timestamp > datetime.utcnow():
                            timestamp_valid = False
                    except (ValueError, KeyError):
                        timestamp_valid = False

                    # Check for suspicious patterns
                    suspicious_indicators = []

                    # Check for rapid sequential actions (possible automation)
                    if len(audit_entries) > 1:
                        current_time = datetime.fromisoformat(
                            entry["timestamp"].replace("Z", "+00:00")
                        )
                        for other_entry in audit_entries:
                            if other_entry != entry and other_entry.get(
                                "user_id"
                            ) == entry.get("user_id"):
                                other_time = datetime.fromisoformat(
                                    other_entry["timestamp"].replace("Z", "+00:00")
                                )
                                time_diff = abs(
                                    (current_time - other_time).total_seconds()
                                )
                                if time_diff < 1:  # Actions within 1 second
                                    suspicious_indicators.append(
                                        "rapid_sequential_actions"
                                    )
                                    break

                    # Check for unusual IP patterns
                    if "ip_address" in entry:
                        ip = entry["ip_address"]
                        if ip and (
                            ip.startswith("0.") or ip.startswith("255.") or "999" in ip
                        ):
                            suspicious_indicators.append("suspicious_ip_address")

                    # Determine overall validity
                    is_valid = (
                        len(missing_fields) == 0
                        and hash_valid
                        and timestamp_valid
                        and len(suspicious_indicators) == 0
                    )

                    if is_valid:
                        valid_entries += 1

                    verification_result = {
                        "entry_id": entry_id,
                        "is_valid": is_valid,
                        "checks": {
                            "required_fields_present": len(missing_fields) == 0,
                            "integrity_hash_valid": hash_valid,
                            "timestamp_valid": timestamp_valid,
                            "no_suspicious_patterns": len(suspicious_indicators) == 0,
                        },
                        "issues": {
                            "missing_fields": missing_fields,
                            "hash_mismatch": not hash_valid,
                            "invalid_timestamp": not timestamp_valid,
                            "suspicious_indicators": suspicious_indicators,
                        },
                    }

                    verification_results.append(verification_result)

                # Calculate integrity score
                integrity_score = (
                    (valid_entries / total_entries * 100) if total_entries > 0 else 100
                )

                # Determine overall status
                if integrity_score == 100:
                    overall_status = "intact"
                elif integrity_score >= 95:
                    overall_status = "minor_issues"
                elif integrity_score >= 80:
                    overall_status = "compromised"
                else:
                    overall_status = "severely_compromised"

                return {
                    "success": True,
                    "verification_results": verification_results,
                    "summary": {
                        "total_entries": total_entries,
                        "valid_entries": valid_entries,
                        "invalid_entries": total_entries - valid_entries,
                        "integrity_score_percent": round(integrity_score, 2),
                        "overall_status": overall_status,
                    },
                }

            except Exception as e:
                return {
                    "success": False,
                    "error": f"Error verifying audit integrity: {str(e)}",
                }

        # Test with valid audit entries
        valid_entries = [
            {
                "audit_id": "audit_20241215_120000_123_1234",
                "timestamp": "2024-12-15T12:00:00",
                "user_id": 123,
                "action": "login",
                "resource_type": "user",
                "integrity_hash": hashlib.sha256(
                    "audit_20241215_120000_123_1234123loginuser2024-12-15T12:00:00".encode()
                ).hexdigest(),
            },
            {
                "audit_id": "audit_20241215_120100_456_5678",
                "timestamp": "2024-12-15T12:01:00",
                "user_id": 456,
                "action": "create_payment",
                "resource_type": "payment",
                "integrity_hash": hashlib.sha256(
                    "audit_20241215_120100_456_5678456create_paymentpayment2024-12-15T12:01:00".encode()
                ).hexdigest(),
            },
        ]

        result = verify_audit_integrity(valid_entries)

        assert result["success"] is True
        assert "verification_results" in result
        assert "summary" in result

        summary = result["summary"]
        assert summary["total_entries"] == 2
        assert summary["valid_entries"] == 2
        assert summary["invalid_entries"] == 0
        assert summary["integrity_score_percent"] == 100.0
        assert summary["overall_status"] == "intact"

        # Check individual verification results
        for verification in result["verification_results"]:
            assert verification["is_valid"] is True
            assert verification["checks"]["required_fields_present"] is True
            assert verification["checks"]["integrity_hash_valid"] is True
            assert verification["checks"]["timestamp_valid"] is True
            assert verification["checks"]["no_suspicious_patterns"] is True

        # Test with compromised audit entries
        compromised_entries = [
            {
                "audit_id": "audit_20241215_120000_123_1234",
                "timestamp": "2024-12-15T12:00:00",
                "user_id": 123,
                "action": "login",
                "resource_type": "user",
                "integrity_hash": "invalid_hash_123",  # Invalid hash
            },
            {
                "audit_id": "audit_20241215_120001_123_5678",  # Same user, 1 second later
                "timestamp": "2024-12-15T12:00:01",
                "user_id": 123,
                "action": "delete_user",
                "resource_type": "user",
                "ip_address": "192.168.1.999",  # Suspicious IP
                "integrity_hash": hashlib.sha256(
                    "audit_20241215_120001_123_5678123delete_useruser2024-12-15T12:00:01".encode()
                ).hexdigest(),
            },
            {
                "audit_id": "audit_20241215_120000_789_9999",
                "timestamp": "2025-01-01T00:00:00",  # Future timestamp
                "user_id": None,  # Missing user_id
                "action": "suspicious_action",
                "resource_type": "system",
            },
        ]

        result = verify_audit_integrity(compromised_entries)

        assert result["success"] is True
        summary = result["summary"]

        # Should detect multiple issues
        assert summary["total_entries"] == 3
        assert summary["valid_entries"] < 3
        assert summary["invalid_entries"] > 0
        assert summary["integrity_score_percent"] < 100
        assert summary["overall_status"] in ["compromised", "severely_compromised"]

        # Check for specific issues
        verification_results = result["verification_results"]

        # First entry should have hash mismatch
        first_result = verification_results[0]
        assert first_result["is_valid"] is False
        assert first_result["issues"]["hash_mismatch"] is True

        # Second entry should have suspicious patterns
        second_result = verification_results[1]
        assert (
            "suspicious_ip_address" in second_result["issues"]["suspicious_indicators"]
            or "rapid_sequential_actions"
            in second_result["issues"]["suspicious_indicators"]
        )

        # Third entry should have missing fields and invalid timestamp
        third_result = verification_results[2]
        assert third_result["is_valid"] is False
        assert "user_id" in third_result["issues"]["missing_fields"]
        assert third_result["issues"]["invalid_timestamp"] is True


@pytest.mark.asyncio
class TestComplianceReporting:
    """Test compliance reporting functionality."""

    def test_generate_compliance_report(self):
        """Test generating compliance reports for audit purposes."""

        def generate_compliance_report(report_type, start_date, end_date, filters=None):
            """
            Generate compliance reports for various regulations
            """
            try:
                # Mock audit data for the date range
                mock_audit_entries = [
                    {
                        "audit_id": "audit_001",
                        "timestamp": "2024-12-01T10:00:00",
                        "user_id": 123,
                        "action": "login",
                        "resource_type": "user",
                        "risk_level": "medium",
                        "compliance_tags": ["PCI-DSS", "SOX"],
                        "ip_address": "192.168.1.100",
                    },
                    {
                        "audit_id": "audit_002",
                        "timestamp": "2024-12-02T14:30:00",
                        "user_id": 456,
                        "action": "data_export",
                        "resource_type": "user_data",
                        "risk_level": "high",
                        "compliance_tags": ["GDPR", "PCI-DSS"],
                        "details": {
                            "exported_records": 1000,
                            "data_types": ["personal", "financial"],
                        },
                    },
                    {
                        "audit_id": "audit_003",
                        "timestamp": "2024-12-03T09:15:00",
                        "user_id": 789,
                        "action": "payment_processed",
                        "resource_type": "payment",
                        "risk_level": "medium",
                        "compliance_tags": ["PCI-DSS"],
                        "details": {
                            "amount": 1000000,
                            "currency": "VND",
                            "payment_method": "credit_card",
                        },
                    },
                    {
                        "audit_id": "audit_004",
                        "timestamp": "2024-12-04T16:45:00",
                        "user_id": 123,
                        "action": "data_deletion",
                        "resource_type": "user_data",
                        "risk_level": "high",
                        "compliance_tags": ["GDPR", "Data-Retention-Policy"],
                        "details": {"deleted_records": 50, "retention_period_days": 30},
                    },
                ]

                # Filter entries by date range
                start_dt = datetime.fromisoformat(start_date)
                end_dt = datetime.fromisoformat(end_date)

                filtered_entries = []
                for entry in mock_audit_entries:
                    entry_dt = datetime.fromisoformat(entry["timestamp"])
                    if start_dt <= entry_dt <= end_dt:
                        # Apply additional filters if provided
                        if filters:
                            if "compliance_tag" in filters and filters[
                                "compliance_tag"
                            ] not in entry.get("compliance_tags", []):
                                continue
                            if (
                                "risk_level" in filters
                                and entry.get("risk_level") != filters["risk_level"]
                            ):
                                continue
                            if (
                                "user_id" in filters
                                and entry.get("user_id") != filters["user_id"]
                            ):
                                continue

                        filtered_entries.append(entry)

                # Generate report based on type
                if report_type == "GDPR":
                    return generate_gdpr_report(filtered_entries, start_date, end_date)
                elif report_type == "PCI-DSS":
                    return generate_pci_dss_report(
                        filtered_entries, start_date, end_date
                    )
                elif report_type == "SOX":
                    return generate_sox_report(filtered_entries, start_date, end_date)
                else:
                    return generate_general_compliance_report(
                        filtered_entries, start_date, end_date
                    )

            except Exception as e:
                return {
                    "success": False,
                    "error": f"Error generating compliance report: {str(e)}",
                }

        def generate_gdpr_report(entries, start_date, end_date):
            """Generate GDPR compliance report"""
            gdpr_entries = [
                e for e in entries if "GDPR" in e.get("compliance_tags", [])
            ]

            # Categorize GDPR-relevant activities
            data_access_events = [
                e for e in gdpr_entries if "access" in e.get("action", "")
            ]
            data_export_events = [
                e for e in gdpr_entries if "export" in e.get("action", "")
            ]
            data_deletion_events = [
                e for e in gdpr_entries if "deletion" in e.get("action", "")
            ]

            # Calculate metrics
            total_data_subjects = len(
                set(e.get("user_id") for e in gdpr_entries if e.get("user_id"))
            )
            total_exported_records = sum(
                e.get("details", {}).get("exported_records", 0)
                for e in data_export_events
            )
            total_deleted_records = sum(
                e.get("details", {}).get("deleted_records", 0)
                for e in data_deletion_events
            )

            # Check compliance violations
            violations = []

            # Check for data exports without proper justification
            for event in data_export_events:
                if not event.get("details", {}).get("justification"):
                    violations.append(
                        {
                            "type": "missing_justification",
                            "event_id": event["audit_id"],
                            "description": "Data export without documented justification",
                        }
                    )

            # Check for data retention violations
            for event in data_deletion_events:
                retention_days = event.get("details", {}).get(
                    "retention_period_days", 0
                )
                if retention_days > 365:  # Example: max 1 year retention
                    violations.append(
                        {
                            "type": "retention_violation",
                            "event_id": event["audit_id"],
                            "description": f"Data retained beyond policy limit: {retention_days} days",
                        }
                    )

            return {
                "success": True,
                "report": {
                    "report_type": "GDPR",
                    "period": {"start_date": start_date, "end_date": end_date},
                    "summary": {
                        "total_events": len(gdpr_entries),
                        "data_subjects_affected": total_data_subjects,
                        "data_access_events": len(data_access_events),
                        "data_export_events": len(data_export_events),
                        "data_deletion_events": len(data_deletion_events),
                        "total_exported_records": total_exported_records,
                        "total_deleted_records": total_deleted_records,
                    },
                    "compliance_status": "compliant"
                    if len(violations) == 0
                    else "violations_found",
                    "violations": violations,
                    "recommendations": [
                        "Ensure all data exports have documented justification",
                        "Review data retention policies for compliance",
                        "Implement automated data deletion for expired records",
                    ],
                },
            }

        def generate_pci_dss_report(entries, start_date, end_date):
            """Generate PCI-DSS compliance report"""
            pci_entries = [
                e for e in entries if "PCI-DSS" in e.get("compliance_tags", [])
            ]

            # Categorize PCI-DSS relevant activities
            payment_events = [
                e for e in pci_entries if "payment" in e.get("action", "")
            ]
            authentication_events = [
                e for e in pci_entries if "login" in e.get("action", "")
            ]

            # Calculate financial metrics
            total_transaction_amount = sum(
                e.get("details", {}).get("amount", 0) for e in payment_events
            )

            # Check for security violations
            violations = []

            # Check for unencrypted payment data (mock check)
            for event in payment_events:
                if event.get("details", {}).get("payment_method") == "credit_card":
                    if not event.get("details", {}).get(
                        "encrypted", True
                    ):  # Assume encrypted by default
                        violations.append(
                            {
                                "type": "unencrypted_data",
                                "event_id": event["audit_id"],
                                "description": "Credit card data processed without encryption",
                            }
                        )

            return {
                "success": True,
                "report": {
                    "report_type": "PCI-DSS",
                    "period": {"start_date": start_date, "end_date": end_date},
                    "summary": {
                        "total_events": len(pci_entries),
                        "payment_transactions": len(payment_events),
                        "authentication_events": len(authentication_events),
                        "total_transaction_amount_vnd": total_transaction_amount,
                    },
                    "compliance_status": "compliant"
                    if len(violations) == 0
                    else "violations_found",
                    "violations": violations,
                    "security_metrics": {
                        "encrypted_transactions_percent": 100,  # Mock: assume all encrypted
                        "failed_authentication_rate": 0.05,  # Mock: 5% failure rate
                        "suspicious_transaction_count": 0,
                    },
                },
            }

        def generate_sox_report(entries, start_date, end_date):
            """Generate SOX compliance report"""
            sox_entries = [e for e in entries if "SOX" in e.get("compliance_tags", [])]

            # Focus on financial controls and access
            financial_access_events = [
                e
                for e in sox_entries
                if e.get("resource_type") in ["payment", "financial_data"]
            ]
            admin_access_events = [
                e for e in sox_entries if "admin" in e.get("action", "")
            ]

            return {
                "success": True,
                "report": {
                    "report_type": "SOX",
                    "period": {"start_date": start_date, "end_date": end_date},
                    "summary": {
                        "total_events": len(sox_entries),
                        "financial_access_events": len(financial_access_events),
                        "administrative_events": len(admin_access_events),
                    },
                    "compliance_status": "compliant",
                    "internal_controls": {
                        "segregation_of_duties": "implemented",
                        "audit_trail_completeness": "100%",
                        "access_controls": "adequate",
                    },
                },
            }

        def generate_general_compliance_report(entries, start_date, end_date):
            """Generate general compliance report"""
            return {
                "success": True,
                "report": {
                    "report_type": "General",
                    "period": {"start_date": start_date, "end_date": end_date},
                    "summary": {
                        "total_events": len(entries),
                        "high_risk_events": len(
                            [e for e in entries if e.get("risk_level") == "high"]
                        ),
                        "unique_users": len(
                            set(e.get("user_id") for e in entries if e.get("user_id"))
                        ),
                    },
                    "compliance_status": "compliant",
                },
            }

        # Test GDPR compliance report
        result = generate_compliance_report(
            report_type="GDPR",
            start_date="2024-12-01T00:00:00",
            end_date="2024-12-31T23:59:59",
            filters={"compliance_tag": "GDPR"},
        )

        assert result["success"] is True
        assert "report" in result

        report = result["report"]
        assert report["report_type"] == "GDPR"
        assert "summary" in report
        assert "compliance_status" in report

        # Check GDPR-specific metrics
        summary = report["summary"]
        assert "data_subjects_affected" in summary
        assert "data_export_events" in summary
        assert "data_deletion_events" in summary
        assert summary["total_exported_records"] >= 0
        assert summary["total_deleted_records"] >= 0

        # Test PCI-DSS compliance report
        result = generate_compliance_report(
            report_type="PCI-DSS",
            start_date="2024-12-01T00:00:00",
            end_date="2024-12-31T23:59:59",
        )

        assert result["success"] is True
        report = result["report"]
        assert report["report_type"] == "PCI-DSS"

        # Check PCI-DSS specific metrics
        summary = report["summary"]
        assert "payment_transactions" in summary
        assert "total_transaction_amount_vnd" in summary
        assert "security_metrics" in report

        security_metrics = report["security_metrics"]
        assert "encrypted_transactions_percent" in security_metrics
        assert "failed_authentication_rate" in security_metrics

        # Test with date range filter
        result = generate_compliance_report(
            report_type="General",
            start_date="2024-12-02T00:00:00",
            end_date="2024-12-03T23:59:59",
        )

        assert result["success"] is True
        report = result["report"]

        # Should only include events within the date range
        assert (
            report["summary"]["total_events"] <= 4
        )  # Max possible events in mock data
