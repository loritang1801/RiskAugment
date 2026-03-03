package com.riskcontrol.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * Prompt Template Entity.
 */
@Entity
@Table(name = "prompt_template")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class PromptTemplate {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false, unique = true, length = 20)
    private String version;  // v1, v2, v3
    
    @Column(nullable = false, columnDefinition = "text")
    private String systemPrompt;
    
    @Column(nullable = false, columnDefinition = "text")
    private String userPromptTemplate;
    
    @Column(columnDefinition = "text")
    private String description;
    
    @Column(nullable = false)
    @Builder.Default
    private Boolean isActive = false;
    
    @Column(name = "avg_response_time_ms")
    private Integer avgResponseTimeMs;
    
    @Column(name = "override_rate", precision = 5, scale = 2)
    private BigDecimal overrideRate;
    
    @CreationTimestamp
    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;
    
    @UpdateTimestamp
    @Column(nullable = false)
    private LocalDateTime updatedAt;
    
    @Column(name = "deleted_at")
    private LocalDateTime deletedAt;
    
    @Version
    @Column(name = "version_num", nullable = false)
    @Builder.Default
    private Integer version_lock = 0;
}
