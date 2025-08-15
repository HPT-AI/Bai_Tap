# ADR-001: Architecture Decision Records Template

## Status
**Proposed** | Accepted | Deprecated | Superseded

## Context
Mô tả ngữ cảnh và vấn đề cần giải quyết. Giải thích tại sao cần đưa ra quyết định kiến trúc này.

## Decision
Mô tả quyết định kiến trúc đã được chọn và lý do tại sao.

## Consequences
### Positive
- Lợi ích và tác động tích cực của quyết định
- Cải thiện về hiệu suất, bảo mật, maintainability

### Negative
- Nhược điểm và trade-offs
- Rủi ro và thách thức tiềm ẩn

### Neutral
- Các tác động trung tính khác

---

# Architecture Decision Records (ADR) Guidelines

## Mục đích
Architecture Decision Records (ADR) là tài liệu ghi lại các quyết định kiến trúc quan trọng trong dự án, bao gồm ngữ cảnh, quyết định và hệ quả.

## Khi nào sử dụng ADR
- Quyết định về công nghệ chính (database, framework, cloud provider)
- Thay đổi kiến trúc hệ thống
- Quyết định về security patterns
- Thay đổi data model quan trọng
- Integration patterns với external services

## Quy trình tạo ADR

### 1. Đặt tên file
```
ADR-XXX-short-description.md
```
**Ví dụ**: `ADR-002-microservices-architecture.md`

### 2. Sử dụng template
Copy template từ `ADR-001-template.md` và điền thông tin

### 3. Review process
- Tạo Pull Request với ADR
- Team review và thảo luận
- Approve và merge khi đồng thuận

### 4. Update status
- **Proposed**: Đang đề xuất, chưa implement
- **Accepted**: Đã chấp nhận và implement
- **Deprecated**: Không còn sử dụng
- **Superseded**: Được thay thế bởi ADR khác

## Template Structure

### Status
Trạng thái hiện tại của ADR:
- **Proposed**: Đang trong quá trình review
- **Accepted**: Đã được chấp nhận và triển khai
- **Deprecated**: Không còn áp dụng
- **Superseded**: Được thay thế bởi ADR mới

### Context
- **Background**: Tình huống hiện tại
- **Problem**: Vấn đề cần giải quyết
- **Requirements**: Yêu cầu kỹ thuật và business
- **Constraints**: Ràng buộc về thời gian, ngân sách, công nghệ

### Decision
- **Solution**: Giải pháp được chọn
- **Alternatives**: Các lựa chọn khác đã xem xét
- **Rationale**: Lý do chọn giải pháp này

### Consequences
- **Positive**: Lợi ích mang lại
- **Negative**: Nhược điểm và trade-offs
- **Neutral**: Tác động trung tính
- **Risks**: Rủi ro tiềm ẩn

## Ví dụ ADR thực tế

---

# ADR-002: Microservices Architecture

## Status
**Accepted**

## Context
Website Dịch vụ Toán học cần xử lý nhiều chức năng khác nhau:
- User management và authentication
- Payment processing với multiple gateways
- Math problem solving với complex algorithms
- Content management system
- Admin dashboard với analytics

**Vấn đề**: Monolithic architecture sẽ khó scale và maintain khi hệ thống phát triển.

**Yêu cầu**:
- Khả năng scale độc lập từng service
- Team có thể phát triển parallel
- Fault isolation giữa các services
- Technology diversity cho từng domain

## Decision
Chọn **Microservices Architecture** với 5 services riêng biệt:

1. **User Service** (Port 8001)
   - Authentication & Authorization
   - User profile management
   - Balance tracking

2. **Payment Service** (Port 8002)
   - VNPay, MoMo, ZaloPay integration
   - Transaction processing
   - Audit logging

3. **Math Solver Service** (Port 8003)
   - Problem solving algorithms
   - Solution caching
   - Pricing logic

4. **Content Service** (Port 8004)
   - CMS functionality
   - FAQ management
   - Multi-language support

5. **Admin Service** (Port 8005)
   - Dashboard & analytics
   - System monitoring
   - User management

**Communication**: HTTP REST APIs với JSON
**Database**: Separate PostgreSQL database per service
**Caching**: Redis với separate databases per service

## Consequences

### Positive
- **Independent Scaling**: Có thể scale Math Solver Service nhiều hơn khi có traffic cao
- **Technology Flexibility**: Có thể sử dụng specialized libraries cho từng domain
- **Team Autonomy**: Mỗi team có thể phát triển và deploy độc lập
- **Fault Isolation**: Lỗi ở Payment Service không ảnh hưởng Math Solver
- **Database Optimization**: Mỗi service có thể optimize database schema riêng

### Negative
- **Complexity**: Tăng complexity về deployment và monitoring
- **Network Latency**: Inter-service communication qua network
- **Data Consistency**: Cần implement distributed transaction patterns
- **Testing**: Integration testing phức tạp hơn
- **Operational Overhead**: Cần monitor nhiều services

### Neutral
- **Learning Curve**: Team cần học distributed systems patterns
- **Infrastructure**: Cần Docker, Kubernetes cho orchestration

### Risks
- **Service Discovery**: Cần implement service discovery mechanism
- **Circuit Breaker**: Cần implement để handle service failures
- **Distributed Tracing**: Cần tools để trace requests across services

---

# ADR-003: Database Per Service Pattern

## Status
**Accepted**

## Context
Với microservices architecture, cần quyết định về database strategy.

**Options considered**:
1. Shared database cho tất cả services
2. Database per service
3. Hybrid approach

## Decision
Chọn **Database per Service** pattern:
- `user_service_db`: Users, sessions, roles, balance
- `payment_service_db`: Transactions, payment methods, logs
- `math_solver_db`: Problems, solutions, statistics
- `content_service_db`: Pages, FAQs, categories
- `admin_service_db`: Admin users, settings, audit logs

## Consequences

### Positive
- **Service Independence**: Mỗi service có full control over data model
- **Technology Diversity**: Có thể chọn database phù hợp (PostgreSQL, MongoDB, etc.)
- **Fault Isolation**: Database failure chỉ ảnh hưởng 1 service
- **Performance**: Optimize database cho từng use case

### Negative
- **Data Consistency**: Không có ACID transactions across services
- **Joins**: Không thể join data across services
- **Operational Complexity**: Cần manage nhiều databases

---

# ADR-004: JWT Authentication Strategy

## Status
**Accepted**

## Context
Cần authentication mechanism cho microservices architecture.

**Requirements**:
- Stateless authentication
- Support for mobile apps
- Token refresh capability
- Role-based access control

## Decision
Implement **JWT (JSON Web Tokens)** với:
- Access token: 1 hour expiry
- Refresh token: 7 days expiry
- RS256 algorithm với public/private key pair
- Claims: user_id, role, permissions

**Token Storage**:
- Access token: Memory/localStorage (frontend)
- Refresh token: HttpOnly cookie

## Consequences

### Positive
- **Stateless**: Không cần session storage
- **Scalable**: Tokens có thể verify ở bất kỳ service nào
- **Mobile Friendly**: Dễ implement cho mobile apps
- **Performance**: Không cần database lookup để verify token

### Negative
- **Token Size**: JWT tokens lớn hơn session IDs
- **Revocation**: Khó revoke tokens trước khi expire
- **Security**: Cần careful handling để tránh XSS/CSRF

---

## ADR Index

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| [ADR-001](ADR-001-template.md) | Template | Accepted | 2024-08-15 |
| [ADR-002](#adr-002-microservices-architecture) | Microservices Architecture | Accepted | 2024-08-15 |
| [ADR-003](#adr-003-database-per-service-pattern) | Database Per Service | Accepted | 2024-08-15 |
| [ADR-004](#adr-004-jwt-authentication-strategy) | JWT Authentication | Accepted | 2024-08-15 |

## Best Practices

### Writing ADRs
1. **Be Concise**: Tập trung vào decision và rationale
2. **Include Context**: Giải thích tại sao cần quyết định này
3. **Consider Alternatives**: Mention các options khác đã xem xét
4. **Document Trade-offs**: Honest về pros và cons
5. **Update Status**: Keep status current khi có thay đổi

### Maintaining ADRs
1. **Regular Review**: Review ADRs trong architecture meetings
2. **Update When Needed**: Update status khi có thay đổi
3. **Link Related ADRs**: Reference các ADRs liên quan
4. **Archive Old ADRs**: Mark deprecated/superseded ADRs

### Team Process
1. **Propose**: Tạo ADR với status "Proposed"
2. **Discuss**: Team review và thảo luận
3. **Decide**: Vote và update status
4. **Implement**: Triển khai decision
5. **Monitor**: Theo dõi consequences và adjust nếu cần

---

**ADR Template Version: 1.0.0**
**Last Updated: 2024-08-15**
