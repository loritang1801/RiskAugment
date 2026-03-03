package com.riskcontrol.controller;

import com.riskcontrol.service.AnalyticsService;
import com.riskcontrol.repository.AIDecisionRecordRepository;
import com.riskcontrol.client.AIClient;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Controller for analytics and statistics.
 */
@Slf4j
@RestController
@RequestMapping("/api/analytics")
@RequiredArgsConstructor
@Tag(name = "Analytics", description = "APIs for analytics and statistics")
public class AnalyticsController {
    
    private final AnalyticsService analyticsService;
    private final AIDecisionRecordRepository aiDecisionRepository;
    private final AIClient aiClient;
    
    @GetMapping("/review-efficiency")
    @Operation(summary = "Get review efficiency statistics")
    public ResponseEntity<Map<String, Object>> getReviewEfficiency(
        @RequestParam(required = false) @DateTimeFormat(pattern = "yyyy-MM-dd HH:mm:ss") LocalDateTime startDate,
        @RequestParam(required = false) @DateTimeFormat(pattern = "yyyy-MM-dd HH:mm:ss") LocalDateTime endDate
    ) {
        log.info("Getting review efficiency statistics");
        
        // Default to last 30 days if not specified
        if (endDate == null) {
            endDate = LocalDateTime.now();
        }
        if (startDate == null) {
            startDate = endDate.minusDays(30);
        }
        
        Map<String, Object> stats = analyticsService.getReviewEfficiency(startDate, endDate);
        
        Map<String, Object> response = new HashMap<>();
        response.put("status", "success");
        response.put("data", stats);
        response.put("startDate", startDate);
        response.put("endDate", endDate);
        
        return ResponseEntity.ok(response);
    }
    
    @GetMapping("/override-rate")
    @Operation(summary = "Get override rate statistics")
    public ResponseEntity<Map<String, Object>> getOverrideRate(
        @RequestParam(required = false) @DateTimeFormat(pattern = "yyyy-MM-dd HH:mm:ss") LocalDateTime startDate,
        @RequestParam(required = false) @DateTimeFormat(pattern = "yyyy-MM-dd HH:mm:ss") LocalDateTime endDate
    ) {
        log.info("Getting override rate statistics");
        
        // Default to last 30 days if not specified
        if (endDate == null) {
            endDate = LocalDateTime.now();
        }
        if (startDate == null) {
            startDate = endDate.minusDays(30);
        }
        
        Map<String, Object> stats = analyticsService.getOverrideRate(startDate, endDate);
        
        Map<String, Object> response = new HashMap<>();
        response.put("status", "success");
        response.put("data", stats);
        response.put("startDate", startDate);
        response.put("endDate", endDate);
        
        return ResponseEntity.ok(response);
    }
    
    @GetMapping("/override-rate-by-version")
    @Operation(summary = "Get override rate by prompt version")
    public ResponseEntity<Map<String, Object>> getOverrideRateByVersion(
        @RequestParam(required = false) @DateTimeFormat(pattern = "yyyy-MM-dd HH:mm:ss") LocalDateTime startDate,
        @RequestParam(required = false) @DateTimeFormat(pattern = "yyyy-MM-dd HH:mm:ss") LocalDateTime endDate
    ) {
        log.info("Getting override rate by version");
        
        // Default to last 30 days if not specified
        if (endDate == null) {
            endDate = LocalDateTime.now();
        }
        if (startDate == null) {
            startDate = endDate.minusDays(30);
        }
        
        Map<String, Object> stats = analyticsService.getOverrideRateByVersion(startDate, endDate);
        
        Map<String, Object> response = new HashMap<>();
        response.put("status", "success");
        response.put("data", stats);
        response.put("startDate", startDate);
        response.put("endDate", endDate);
        
        return ResponseEntity.ok(response);
    }
    
    @GetMapping("/prompt-comparison")
    @Operation(summary = "Get prompt version comparison analysis")
    public ResponseEntity<Map<String, Object>> getPromptComparison(
        @RequestParam(required = false) @DateTimeFormat(pattern = "yyyy-MM-dd HH:mm:ss") LocalDateTime startDate,
        @RequestParam(required = false) @DateTimeFormat(pattern = "yyyy-MM-dd HH:mm:ss") LocalDateTime endDate
    ) {
        log.info("Getting prompt version comparison");
        
        // Default to last 30 days if not specified
        if (endDate == null) {
            endDate = LocalDateTime.now();
        }
        if (startDate == null) {
            startDate = endDate.minusDays(30);
        }
        
        Map<String, Object> comparison = analyticsService.getPromptVersionComparison(startDate, endDate);
        
        Map<String, Object> response = new HashMap<>();
        response.put("status", "success");
        response.put("data", comparison);
        response.put("startDate", startDate);
        response.put("endDate", endDate);
        
        return ResponseEntity.ok(response);
    }
    
    @GetMapping("/review-efficiency-trend")
    @Operation(summary = "Get review efficiency trend")
    public ResponseEntity<Map<String, Object>> getReviewEfficiencyTrend(
        @RequestParam(required = false) @DateTimeFormat(pattern = "yyyy-MM-dd HH:mm:ss") LocalDateTime startDate,
        @RequestParam(required = false) @DateTimeFormat(pattern = "yyyy-MM-dd HH:mm:ss") LocalDateTime endDate,
        @RequestParam(defaultValue = "day") String interval
    ) {
        log.info("Getting review efficiency trend with interval: {}", interval);
        
        // Default to last 30 days if not specified
        if (endDate == null) {
            endDate = LocalDateTime.now();
        }
        if (startDate == null) {
            startDate = endDate.minusDays(30);
        }
        
        Map<String, Object> trend = analyticsService.getReviewEfficiencyTrend(startDate, endDate, interval);
        
        Map<String, Object> response = new HashMap<>();
        response.put("status", "success");
        response.put("data", trend);
        response.put("startDate", startDate);
        response.put("endDate", endDate);
        response.put("interval", interval);
        
        return ResponseEntity.ok(response);
    }
    
    @GetMapping("/override-rate-trend")
    @Operation(summary = "Get override rate trend")
    public ResponseEntity<Map<String, Object>> getOverrideRateTrend(
        @RequestParam(required = false) @DateTimeFormat(pattern = "yyyy-MM-dd HH:mm:ss") LocalDateTime startDate,
        @RequestParam(required = false) @DateTimeFormat(pattern = "yyyy-MM-dd HH:mm:ss") LocalDateTime endDate
    ) {
        log.info("Getting override rate trend");
        
        // Default to last 30 days if not specified
        if (endDate == null) {
            endDate = LocalDateTime.now();
        }
        if (startDate == null) {
            startDate = endDate.minusDays(30);
        }
        
        Map<String, Object> trend = analyticsService.getOverrideRateTrend(startDate, endDate);
        
        Map<String, Object> response = new HashMap<>();
        response.put("status", "success");
        response.put("data", trend);
        response.put("startDate", startDate);
        response.put("endDate", endDate);
        
        return ResponseEntity.ok(response);
    }

    @GetMapping("/chain-health")
    @Operation(summary = "Get AI analysis chain health metrics")
    public ResponseEntity<Map<String, Object>> getChainHealth(
        @RequestParam(defaultValue = "200") int limit
    ) {
        log.info("Getting AI chain health metrics, limit={}", limit);

        Map<String, Object> metrics = aiClient.getChainHealthMetrics(limit);

        Map<String, Object> response = new HashMap<>();
        response.put("status", "success");
        response.put("data", metrics);
        return ResponseEntity.ok(response);
    }
}
