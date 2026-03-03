package com.riskcontrol.service;

import com.riskcontrol.repository.AIDecisionRecordRepository;
import com.riskcontrol.repository.CaseAuditLogRepository;
import com.riskcontrol.repository.PromptTemplateRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.sql.Date;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;

/**
 * Service for analytics and statistics.
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class AnalyticsService {
    
    private final AIDecisionRecordRepository aiDecisionRepository;
    private final CaseAuditLogRepository auditLogRepository;
    private final PromptTemplateRepository promptTemplateRepository;
    
    /**
     * Get review efficiency statistics.
     */
    public Map<String, Object> getReviewEfficiency(LocalDateTime startDate, LocalDateTime endDate) {
        log.info("Getting review efficiency from {} to {}", startDate, endDate);
        
        // Get all AI decision records in date range
        List<Object[]> results = aiDecisionRepository.getReviewEfficiencyStats(startDate, endDate);
        
        Map<String, Object> stats = new HashMap<>();
        
        if (results.isEmpty()) {
            stats.put("averageReviewTime", 0);
            stats.put("totalCases", 0);
            stats.put("minTime", 0);
            stats.put("maxTime", 0);
            return stats;
        }
        
        Object[] result = results.get(0);
        stats.put("averageReviewTime", result[0] != null ? ((Number) result[0]).longValue() : 0);
        stats.put("totalCases", result[1] != null ? ((Number) result[1]).longValue() : 0);
        stats.put("minTime", result[2] != null ? ((Number) result[2]).longValue() : 0);
        stats.put("maxTime", result[3] != null ? ((Number) result[3]).longValue() : 0);
        
        return stats;
    }
    
    /**
     * Get override rate statistics.
     */
    public Map<String, Object> getOverrideRate(LocalDateTime startDate, LocalDateTime endDate) {
        log.info("Getting override rate from {} to {}", startDate, endDate);
        
        List<Object[]> results = aiDecisionRepository.getOverrideRateStats(startDate, endDate);
        
        Map<String, Object> stats = new HashMap<>();
        
        if (results.isEmpty()) {
            stats.put("overrideRate", 0.0);
            stats.put("totalDecisions", 0);
            stats.put("overrideCount", 0);
            return stats;
        }
        
        Object[] result = results.get(0);
        long totalDecisions = result[0] != null ? ((Number) result[0]).longValue() : 0;
        long overrideCount = result[1] != null ? ((Number) result[1]).longValue() : 0;
        
        double overrideRate = totalDecisions > 0 ? (double) overrideCount / totalDecisions : 0.0;
        
        stats.put("overrideRate", overrideRate);
        stats.put("totalDecisions", totalDecisions);
        stats.put("overrideCount", overrideCount);
        
        return stats;
    }
    
    /**
     * Get override rate by prompt version.
     */
    public Map<String, Object> getOverrideRateByVersion(LocalDateTime startDate, LocalDateTime endDate) {
        log.info("Getting override rate by version from {} to {}", startDate, endDate);
        
        List<Object[]> results = aiDecisionRepository.getOverrideRateByVersion(startDate, endDate);
        
        Map<String, Object> versionStats = new HashMap<>();
        
        for (Object[] result : results) {
            String version = (String) result[0];
            long totalDecisions = result[1] != null ? ((Number) result[1]).longValue() : 0;
            long overrideCount = result[2] != null ? ((Number) result[2]).longValue() : 0;
            
            double overrideRate = totalDecisions > 0 ? (double) overrideCount / totalDecisions : 0.0;
            
            Map<String, Object> stats = new HashMap<>();
            stats.put("version", version);
            stats.put("overrideRate", overrideRate);
            stats.put("totalDecisions", totalDecisions);
            stats.put("overrideCount", overrideCount);
            
            versionStats.put(version, stats);
        }
        
        return versionStats;
    }
    
    /**
     * Get prompt version comparison analysis.
     */
    public Map<String, Object> getPromptVersionComparison(LocalDateTime startDate, LocalDateTime endDate) {
        log.info("Getting prompt version comparison from {} to {}", startDate, endDate);
        
        try {
            List<Object[]> results = aiDecisionRepository.getPromptVersionComparison(startDate, endDate);
            log.info("Query returned {} rows", results.size());
            
            Map<String, Object> comparison = new HashMap<>();
            List<Map<String, Object>> versions = new ArrayList<>();
            
            for (Object[] result : results) {
                String version = (String) result[0];
                long totalCases = result[1] != null ? ((Number) result[1]).longValue() : 0;
                long approvedCases = result[2] != null ? ((Number) result[2]).longValue() : 0;
                long rejectedCases = result[3] != null ? ((Number) result[3]).longValue() : 0;
                long overrideCases = result[4] != null ? ((Number) result[4]).longValue() : 0;
                long avgTime = result[5] != null ? ((Number) result[5]).longValue() : 0;
                
                log.info("Processing version: {}, totalCases: {}, approvedCases: {}, rejectedCases: {}, overrideCases: {}, avgTime: {}", 
                    version, totalCases, approvedCases, rejectedCases, overrideCases, avgTime);
                
                double approvalRate = totalCases > 0 ? (double) approvedCases / totalCases : 0.0;
                double rejectionRate = totalCases > 0 ? (double) rejectedCases / totalCases : 0.0;
                double overrideRate = totalCases > 0 ? (double) overrideCases / totalCases : 0.0;
                
                Map<String, Object> versionData = new HashMap<>();
                versionData.put("version", version);
                versionData.put("totalCases", totalCases);
                versionData.put("approvedCases", approvedCases);
                versionData.put("rejectedCases", rejectedCases);
                versionData.put("overrideCases", overrideCases);
                versionData.put("approvalRate", approvalRate);
                versionData.put("rejectionRate", rejectionRate);
                versionData.put("overrideRate", overrideRate);
                versionData.put("averageReviewTime", avgTime);
                
                versions.add(versionData);
            }
            
            comparison.put("versions", versions);
            comparison.put("count", versions.size());
            log.info("Returning {} versions", versions.size());
            
            return comparison;
        } catch (Exception e) {
            log.error("Error getting prompt version comparison", e);
            // Return empty comparison on error
            Map<String, Object> comparison = new HashMap<>();
            comparison.put("versions", new ArrayList<>());
            comparison.put("count", 0);
            return comparison;
        }
    }
    
    /**
     * Get review efficiency trend.
     */
    public Map<String, Object> getReviewEfficiencyTrend(LocalDateTime startDate, LocalDateTime endDate, String interval) {
        log.info("Getting review efficiency trend from {} to {} with interval {}", startDate, endDate, interval);
        
        List<Object[]> results = aiDecisionRepository.getReviewEfficiencyTrend(startDate, endDate);
        
        Map<String, Object> trend = new HashMap<>();
        List<Map<String, Object>> data = new ArrayList<>();
        
        for (Object[] result : results) {
            LocalDate date = toLocalDate(result[0]);
            long avgTime = result[1] != null ? ((Number) result[1]).longValue() : 0;
            long count = result[2] != null ? ((Number) result[2]).longValue() : 0;
            
            Map<String, Object> point = new HashMap<>();
            point.put("date", date);
            point.put("averageTime", avgTime);
            point.put("count", count);
            
            data.add(point);
        }
        
        trend.put("data", data);
        trend.put("count", data.size());
        
        return trend;
    }
    
    /**
     * Get override rate trend.
     */
    public Map<String, Object> getOverrideRateTrend(LocalDateTime startDate, LocalDateTime endDate) {
        log.info("Getting override rate trend from {} to {}", startDate, endDate);
        
        List<Object[]> results = aiDecisionRepository.getOverrideRateTrend(startDate, endDate);
        
        Map<String, Object> trend = new HashMap<>();
        List<Map<String, Object>> data = new ArrayList<>();
        
        for (Object[] result : results) {
            LocalDate date = toLocalDate(result[0]);
            long totalDecisions = result[1] != null ? ((Number) result[1]).longValue() : 0;
            long overrideCount = result[2] != null ? ((Number) result[2]).longValue() : 0;
            
            double overrideRate = totalDecisions > 0 ? (double) overrideCount / totalDecisions : 0.0;
            
            Map<String, Object> point = new HashMap<>();
            point.put("date", date);
            point.put("overrideRate", overrideRate);
            point.put("totalDecisions", totalDecisions);
            point.put("overrideCount", overrideCount);
            
            data.add(point);
        }
        
        trend.put("data", data);
        trend.put("count", data.size());
        
        return trend;
    }

    private LocalDate toLocalDate(Object value) {
        if (value == null) {
            return null;
        }
        if (value instanceof LocalDate localDate) {
            return localDate;
        }
        if (value instanceof LocalDateTime localDateTime) {
            return localDateTime.toLocalDate();
        }
        if (value instanceof Date sqlDate) {
            return sqlDate.toLocalDate();
        }
        if (value instanceof java.util.Date utilDate) {
            return new Date(utilDate.getTime()).toLocalDate();
        }
        if (value instanceof String stringValue) {
            try {
                return LocalDate.parse(stringValue.trim());
            } catch (Exception ignored) {
                return null;
            }
        }
        return null;
    }
}
