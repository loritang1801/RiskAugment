package com.riskcontrol.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.util.List;
import java.util.Map;

/**
 * DTO for AI analysis result.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AIAnalysisDTO {
    
    @JsonProperty("risk_level")
    private String riskLevel;
    
    @JsonProperty("confidence_score")
    private BigDecimal confidenceScore;
    
    @JsonProperty("key_risk_points")
    private List<String> keyRiskPoints;
    
    @JsonProperty("suggested_action")
    private String suggestedAction;
    
    private String reasoning;
    
    @JsonProperty("similar_cases_analysis")
    private String similarCasesAnalysis;
    
    @JsonProperty("rule_engine_alignment")
    private String ruleEngineAlignment;

    @JsonProperty("similar_cases_details")
    private List<Map<String, Object>> similarCasesDetails;
    
    @JsonProperty("confidence_explanation")
    private String confidenceExplanation;
    
    private List<String> uncertainties;
    
    @JsonProperty("alternative_view")
    private String alternativeView;
    
    private Map<String, Object> metadata;
    
    @JsonProperty("analysis_source")
    private String analysisSource;
    
    @JsonProperty("analysis_model")
    private String analysisModel;

    @JsonProperty("total_time_ms")
    private Integer totalTimeMs;
}
