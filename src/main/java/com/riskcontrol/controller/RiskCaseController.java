package com.riskcontrol.controller;

import com.riskcontrol.dto.AIAnalysisDTO;
import com.riskcontrol.dto.RiskCaseDTO;
import com.riskcontrol.dto.request.CreateRiskCaseRequest;
import com.riskcontrol.service.AIService;
import com.riskcontrol.service.RiskCaseService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@Slf4j
@RestController
@RequestMapping("/api/cases")
@RequiredArgsConstructor
@Tag(name = "Risk Case Management", description = "APIs for risk case management")
public class RiskCaseController {
    
    private final RiskCaseService riskCaseService;
    private final AIService aiService;
    
    @PostMapping
    @Operation(summary = "Create a new risk case")
    public ResponseEntity<Map<String, Object>> createRiskCase(@Valid @RequestBody CreateRiskCaseRequest request) {
        log.info("Creating risk case: {}", request.getBizTransactionId());
        
        RiskCaseDTO riskCaseDTO = riskCaseService.createRiskCase(request);
        
        Map<String, Object> response = new HashMap<>();
        response.put("status", "success");
        response.put("data", riskCaseDTO);
        
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }
    
    @GetMapping("/{id}")
    @Operation(summary = "Get risk case by ID")
    public ResponseEntity<Map<String, Object>> getRiskCaseById(@PathVariable Long id) {
        log.info("Getting risk case: {}", id);
        
        RiskCaseDTO riskCaseDTO = riskCaseService.getRiskCaseById(id);
        
        Map<String, Object> response = new HashMap<>();
        response.put("status", "success");
        response.put("data", riskCaseDTO);
        
        return ResponseEntity.ok(response);
    }
    
    @GetMapping("/transaction/{bizTransactionId}")
    @Operation(summary = "Get risk case by business transaction ID")
    public ResponseEntity<Map<String, Object>> getRiskCaseByBizTransactionId(@PathVariable String bizTransactionId) {
        log.info("Getting risk case by transaction ID: {}", bizTransactionId);
        
        RiskCaseDTO riskCaseDTO = riskCaseService.getRiskCaseByBizTransactionId(bizTransactionId);
        
        Map<String, Object> response = new HashMap<>();
        response.put("status", "success");
        response.put("data", riskCaseDTO);
        
        return ResponseEntity.ok(response);
    }
    
    @GetMapping
    @Operation(summary = "List all risk cases")
    public ResponseEntity<Map<String, Object>> listRiskCases(
        @RequestParam(defaultValue = "0") int page,
        @RequestParam(defaultValue = "20") int size,
        @RequestParam(required = false) String bizTransactionId,
        @RequestParam(required = false) String status,
        @RequestParam(required = false) String riskLevel,
        @RequestParam(required = false) String country
    ) {
        log.info("Listing risk cases - page: {}, size: {}, bizTransactionId: {}, status: {}, riskLevel: {}, country: {}", 
            page, size, bizTransactionId, status, riskLevel, country);
        
        Page<RiskCaseDTO> cases;
        
        // If any filter is provided, use search method
        if ((bizTransactionId != null && !bizTransactionId.isEmpty()) ||
            (status != null && !status.isEmpty()) ||
            (riskLevel != null && !riskLevel.isEmpty()) ||
            (country != null && !country.isEmpty())) {
            cases = riskCaseService.searchRiskCases(bizTransactionId, status, riskLevel, country, page, size);
        } else {
            cases = riskCaseService.listRiskCases(page, size);
        }
        
        Map<String, Object> response = new HashMap<>();
        response.put("status", "success");
        response.put("data", cases.getContent());
        response.put("total", cases.getTotalElements());
        response.put("page", page);
        response.put("size", size);
        response.put("totalPages", cases.getTotalPages());
        
        return ResponseEntity.ok(response);
    }
    
    @GetMapping("/status/{status}")
    @Operation(summary = "List risk cases by status")
    public ResponseEntity<Map<String, Object>> listRiskCasesByStatus(
        @PathVariable String status,
        @RequestParam(defaultValue = "0") int page,
        @RequestParam(defaultValue = "20") int size
    ) {
        log.info("Listing risk cases by status: {} - page: {}, size: {}", status, page, size);
        
        Page<RiskCaseDTO> cases = riskCaseService.listRiskCasesByStatus(status, page, size);
        
        Map<String, Object> response = new HashMap<>();
        response.put("status", "success");
        response.put("data", cases.getContent());
        response.put("total", cases.getTotalElements());
        response.put("page", page);
        response.put("size", size);
        response.put("totalPages", cases.getTotalPages());
        
        return ResponseEntity.ok(response);
    }
    
    @GetMapping("/risk-level/{riskLevel}")
    @Operation(summary = "List risk cases by risk level")
    public ResponseEntity<Map<String, Object>> listRiskCasesByRiskLevel(
        @PathVariable String riskLevel,
        @RequestParam(defaultValue = "0") int page,
        @RequestParam(defaultValue = "20") int size
    ) {
        log.info("Listing risk cases by risk level: {} - page: {}, size: {}", riskLevel, page, size);
        
        Page<RiskCaseDTO> cases = riskCaseService.listRiskCasesByRiskLevel(riskLevel, page, size);
        
        Map<String, Object> response = new HashMap<>();
        response.put("status", "success");
        response.put("data", cases.getContent());
        response.put("total", cases.getTotalElements());
        response.put("page", page);
        response.put("size", size);
        response.put("totalPages", cases.getTotalPages());
        
        return ResponseEntity.ok(response);
    }
    
    @GetMapping("/pending")
    @Operation(summary = "List pending risk cases")
    public ResponseEntity<Map<String, Object>> listPendingRiskCases(
        @RequestParam(defaultValue = "0") int page,
        @RequestParam(defaultValue = "20") int size
    ) {
        log.info("Listing pending risk cases - page: {}, size: {}", page, size);
        
        Page<RiskCaseDTO> cases = riskCaseService.listPendingRiskCases(page, size);
        
        Map<String, Object> response = new HashMap<>();
        response.put("status", "success");
        response.put("data", cases.getContent());
        response.put("total", cases.getTotalElements());
        response.put("page", page);
        response.put("size", size);
        response.put("totalPages", cases.getTotalPages());
        
        return ResponseEntity.ok(response);
    }
    
    @PutMapping("/{id}")
    @Operation(summary = "Update risk case")
    public ResponseEntity<Map<String, Object>> updateRiskCase(
        @PathVariable Long id,
        @Valid @RequestBody CreateRiskCaseRequest request
    ) {
        log.info("Updating risk case: {}", id);
        
        RiskCaseDTO riskCaseDTO = riskCaseService.updateRiskCase(id, request);
        
        Map<String, Object> response = new HashMap<>();
        response.put("status", "success");
        response.put("data", riskCaseDTO);
        
        return ResponseEntity.ok(response);
    }
    
    @PutMapping("/{id}/status/{status}")
    @Operation(summary = "Update risk case status")
    public ResponseEntity<Map<String, Object>> updateRiskCaseStatus(
        @PathVariable Long id,
        @PathVariable String status
    ) {
        log.info("Updating risk case status: {} -> {}", id, status);
        
        RiskCaseDTO riskCaseDTO = riskCaseService.updateRiskCaseStatus(id, status);
        
        Map<String, Object> response = new HashMap<>();
        response.put("status", "success");
        response.put("data", riskCaseDTO);
        
        return ResponseEntity.ok(response);
    }
    
    @PutMapping("/{id}/approve")
    @Operation(summary = "Approve risk case")
    public ResponseEntity<Map<String, Object>> approveRiskCase(@PathVariable Long id) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        String username = authentication != null ? authentication.getName() : null;
        log.info("Approving risk case: {} by reviewer(username): {}", id, username);

        RiskCaseDTO riskCaseDTO = riskCaseService.approveRiskCase(id, username);
        
        Map<String, Object> response = new HashMap<>();
        response.put("status", "success");
        response.put("data", riskCaseDTO);
        
        return ResponseEntity.ok(response);
    }
    
    @PutMapping("/{id}/reject")
    @Operation(summary = "Reject risk case")
    public ResponseEntity<Map<String, Object>> rejectRiskCase(@PathVariable Long id) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        String username = authentication != null ? authentication.getName() : null;
        log.info("Rejecting risk case: {} by reviewer(username): {}", id, username);

        RiskCaseDTO riskCaseDTO = riskCaseService.rejectRiskCase(id, username);
        
        Map<String, Object> response = new HashMap<>();
        response.put("status", "success");
        response.put("data", riskCaseDTO);
        
        return ResponseEntity.ok(response);
    }
    
    @DeleteMapping("/{id}")
    @Operation(summary = "Delete risk case")
    public ResponseEntity<Map<String, Object>> deleteRiskCase(@PathVariable Long id) {
        log.info("Deleting risk case: {}", id);
        
        riskCaseService.deleteRiskCase(id);
        
        Map<String, Object> response = new HashMap<>();
        response.put("status", "success");
        response.put("message", "Risk case deleted successfully");
        
        return ResponseEntity.ok(response);
    }
    
    @PostMapping("/{id}/analyze")
    @Operation(summary = "Analyze risk case using AI")
    public ResponseEntity<Map<String, Object>> analyzeRiskCase(
        @PathVariable Long id,
        @RequestParam(required = false) String promptVersion
    ) {
        log.info("Analyzing risk case: {} with prompt version: {}", id, promptVersion);
        
        AIAnalysisDTO analysis = aiService.analyzeCase(id, promptVersion);
        
        // Convert DTO to map to ensure all fields are included
        Map<String, Object> analysisMap = new HashMap<>();
        analysisMap.put("risk_level", analysis.getRiskLevel());
        analysisMap.put("confidence_score", analysis.getConfidenceScore());
        analysisMap.put("suggested_action", analysis.getSuggestedAction());
        analysisMap.put("key_risk_points", analysis.getKeyRiskPoints());
        analysisMap.put("reasoning", analysis.getReasoning());
        analysisMap.put("similar_cases_analysis", analysis.getSimilarCasesAnalysis());
        analysisMap.put("similar_cases_details", analysis.getSimilarCasesDetails());
        analysisMap.put("rule_engine_alignment", analysis.getRuleEngineAlignment());
        analysisMap.put("analysis_source", analysis.getAnalysisSource());
        analysisMap.put("analysis_model", analysis.getAnalysisModel());
        analysisMap.put("total_time_ms", analysis.getTotalTimeMs());
        analysisMap.put("metadata", analysis.getMetadata());
        
        Map<String, Object> response = new HashMap<>();
        response.put("status", "success");
        response.put("data", analysisMap);
        
        return ResponseEntity.ok(response);
    }
    
}
