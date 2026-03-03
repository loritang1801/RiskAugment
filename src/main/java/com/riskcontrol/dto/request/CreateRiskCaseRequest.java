package com.riskcontrol.dto.request;

import com.fasterxml.jackson.databind.JsonNode;
import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class CreateRiskCaseRequest {
    
    @NotBlank(message = "Business transaction ID is required")
    private String bizTransactionId;
    
    @NotNull(message = "Amount is required")
    @DecimalMin(value = "0.01", message = "Amount must be greater than 0")
    private BigDecimal amount;
    
    @NotBlank(message = "Currency is required")
    private String currency;
    
    private String country;
    private String deviceRisk;
    private String userLabel;
    
    @NotNull(message = "Risk features are required")
    private JsonNode riskFeatures;
    
    private BigDecimal ruleEngineScore;
    private JsonNode triggeredRules;
    private BigDecimal riskScore;
    private String riskLevel;
    
    @NotBlank(message = "Risk status is required")
    private String riskStatus;
}
