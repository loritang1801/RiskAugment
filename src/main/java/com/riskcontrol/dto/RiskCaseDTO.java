package com.riskcontrol.dto;

import com.fasterxml.jackson.databind.JsonNode;
import com.riskcontrol.entity.RiskCase;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.Hibernate;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class RiskCaseDTO {
    
    private Long id;
    private String bizTransactionId;
    private BigDecimal amount;
    private String currency;
    private String country;
    private String deviceRisk;
    private String userLabel;
    private JsonNode riskFeatures;
    private BigDecimal ruleEngineScore;
    private JsonNode triggeredRules;
    private BigDecimal riskScore;
    private String riskLevel;
    private String riskStatus;
    private Long aiDecisionId;
    private String finalDecision;
    private Long reviewerId;
    private String reviewerName;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
    
    public static RiskCaseDTO from(RiskCase riskCase) {
        return RiskCaseDTO.builder()
            .id(riskCase.getId())
            .bizTransactionId(riskCase.getBizTransactionId())
            .amount(riskCase.getAmount())
            .currency(riskCase.getCurrency())
            .country(riskCase.getCountry())
            .deviceRisk(riskCase.getDeviceRisk())
            .userLabel(riskCase.getUserLabel())
            .riskFeatures(riskCase.getRiskFeatures())
            .ruleEngineScore(riskCase.getRuleEngineScore())
            .triggeredRules(riskCase.getTriggeredRules())
            .riskScore(riskCase.getRiskScore())
            .riskLevel(riskCase.getRiskLevel())
            .riskStatus(riskCase.getRiskStatus())
            .aiDecisionId(riskCase.getAiDecisionId())
            .finalDecision(riskCase.getFinalDecision())
            .reviewerId(riskCase.getReviewerId())
            .reviewerName(
                riskCase.getReviewer() != null && Hibernate.isInitialized(riskCase.getReviewer())
                    ? riskCase.getReviewer().getUsername()
                    : null
            )
            .createdAt(riskCase.getCreatedAt())
            .updatedAt(riskCase.getUpdatedAt())
            .build();
    }
}
