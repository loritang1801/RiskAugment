package com.riskcontrol.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serializable;
import java.time.LocalDateTime;

/**
 * 数据分析 DTO
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AnalyticsDTO implements Serializable {
    
    private static final long serialVersionUID = 1L;
    
    /**
     * 平均响应时间（毫秒）
     */
    private Double averageResponseTime;
    
    /**
     * 总数
     */
    private Long totalCount;
    
    /**
     * 最小响应时间（毫秒）
     */
    private Long minResponseTime;
    
    /**
     * 最大响应时间（毫秒）
     */
    private Long maxResponseTime;
    
    /**
     * Override 率
     */
    private Double overrideRate;
    
    /**
     * Override 数量
     */
    private Long overrideCount;
    
    /**
     * 时间范围开始
     */
    private LocalDateTime startDate;
    
    /**
     * 时间范围结束
     */
    private LocalDateTime endDate;
    
    /**
     * Prompt 版本
     */
    private String promptVersion;
    
    /**
     * 审核效率统计
     */
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class ReviewEfficiency implements Serializable {
        private static final long serialVersionUID = 1L;
        
        private Long totalCases;
        private Long averageReviewTime;
        private Long minReviewTime;
        private Long maxReviewTime;
    }
    
    /**
     * Override 率统计
     */
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class OverrideRate implements Serializable {
        private static final long serialVersionUID = 1L;
        
        private Long totalCases;
        private Long overrideCases;
        private Double overridePercentage;
    }
}
