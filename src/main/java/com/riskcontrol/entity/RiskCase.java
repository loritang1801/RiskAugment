package com.riskcontrol.entity;

import com.fasterxml.jackson.databind.JsonNode;
import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.annotations.UpdateTimestamp;
import org.hibernate.type.SqlTypes;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity
@Table(name = "risk_case")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class RiskCase {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false, unique = true, length = 64)
    private String bizTransactionId;
    
    @Column(nullable = false, precision = 18, scale = 2)
    private BigDecimal amount;
    
    @Column(nullable = false, length = 10)
    private String currency;
    
    @Column(length = 10)
    private String country;
    
    @Column(length = 20)
    private String deviceRisk;  // LOW, MEDIUM, HIGH
    
    @Column(length = 50)
    private String userLabel;  // new_user, existing_user, vip_user
    
    @JdbcTypeCode(SqlTypes.JSON)
    @Column(nullable = false, columnDefinition = "jsonb")
    private JsonNode riskFeatures;
    
    @Column(precision = 5, scale = 2)
    private BigDecimal ruleEngineScore;
    
    @JdbcTypeCode(SqlTypes.JSON)
    @Column(columnDefinition = "jsonb")
    private JsonNode triggeredRules;
    
    @Column(precision = 5, scale = 2)
    private BigDecimal riskScore;
    
    @Column(length = 20)
    private String riskLevel;  // LOW, MEDIUM, HIGH
    
    @Column(nullable = false, length = 30)
    private String riskStatus;  // PENDING, ANALYZING, APPROVED, REJECTED
    
    @Column(name = "ai_decision_id")
    private Long aiDecisionId;
    
    @Column(length = 20)
    private String finalDecision;  // APPROVE, REJECT
    
    @Column(name = "reviewer_id")
    private Long reviewerId;
    
    @Column(name = "user_id")
    private Long userId;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "reviewer_id", insertable = false, updatable = false)
    private User reviewer;
    
    @CreationTimestamp
    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;
    
    @UpdateTimestamp
    @Column(nullable = false)
    private LocalDateTime updatedAt;
    
    @Column(name = "deleted_at")
    private LocalDateTime deletedAt;
    
    @Version
    @Column(nullable = false)
    @Builder.Default
    private Integer version = 0;
}
