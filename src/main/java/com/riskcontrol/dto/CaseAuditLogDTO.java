package com.riskcontrol.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.Map;

/**
 * DTO for Case Audit Log.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CaseAuditLogDTO {
    
    private Long id;
    
    @JsonProperty("case_id")
    private Long caseId;
    
    @JsonProperty("operator_id")
    private Long operatorId;
    
    @JsonProperty("operator_name")
    private String operatorName;
    
    private String operation;
    
    private String description;
    
    @JsonProperty("old_value")
    private Map<String, Object> oldValue;
    
    @JsonProperty("new_value")
    private Map<String, Object> newValue;
    
    @JsonProperty("created_at")
    private LocalDateTime createdAt;
}
