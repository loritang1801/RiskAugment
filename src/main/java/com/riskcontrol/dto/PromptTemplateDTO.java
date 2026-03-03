package com.riskcontrol.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * DTO for Prompt Template.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class PromptTemplateDTO {
    
    private Long id;
    
    private String version;
    
    @JsonProperty("system_prompt")
    private String systemPrompt;
    
    @JsonProperty("user_prompt_template")
    private String userPromptTemplate;
    
    private String description;
    
    @JsonProperty("is_active")
    private Boolean isActive;
    
    @JsonProperty("avg_response_time_ms")
    private Integer avgResponseTimeMs;
    
    @JsonProperty("override_rate")
    private BigDecimal overrideRate;
    
    @JsonProperty("created_at")
    private LocalDateTime createdAt;
    
    @JsonProperty("updated_at")
    private LocalDateTime updatedAt;
}
