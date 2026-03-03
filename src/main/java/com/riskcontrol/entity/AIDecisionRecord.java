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
@Table(name = "ai_decision_record")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class AIDecisionRecord {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(name = "case_id", nullable = false)
    private Long caseId;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "case_id", insertable = false, updatable = false)
    private RiskCase riskCase;
    
    @Column(nullable = false, length = 20)
    private String promptVersion;
    
    @Column(length = 20)
    private String riskLevel;
    
    @Column(precision = 5, scale = 2)
    private BigDecimal confidenceScore;
    
    @Column(length = 20)
    private String suggestedAction;
    
    @Column(columnDefinition = "text")
    private String keyRiskPoints;
    
    @Column(columnDefinition = "text")
    private String reasoning;
    
    @Column(columnDefinition = "text")
    private String similarCasesAnalysis;

    @Column(columnDefinition = "text")
    private String similarCasesDetails;
    
    @Column(columnDefinition = "text")
    private String ruleEngineAlignment;
    
    @Column(nullable = false)
    @Builder.Default
    private Boolean overrideFlag = false;
    
    @Column(columnDefinition = "text")
    private String overrideReason;
    
    @Column(length = 20)
    private String finalDecision;
    
    @Column(name = "retrieval_time_ms")
    private Integer retrievalTimeMs;
    
    @Column(name = "llm_call_time_ms")
    private Integer llmCallTimeMs;
    
    @Column(name = "total_time_ms")
    private Integer totalTimeMs;
    
    @Column(name = "analysis_source", length = 50)
    private String analysisSource;
    
    @Column(name = "analysis_model", length = 100)
    private String analysisModel;
    
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
