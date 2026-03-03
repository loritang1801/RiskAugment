package com.riskcontrol.controller;

import com.riskcontrol.dto.CaseAuditLogDTO;
import com.riskcontrol.service.CaseAuditLogService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Controller for Case Audit Log management.
 */
@Slf4j
@RestController
@RequestMapping("/api/cases")
@RequiredArgsConstructor
@Tag(name = "Case Audit Log", description = "APIs for case audit log management")
public class CaseAuditLogController {
    
    private final CaseAuditLogService auditLogService;
    
    @GetMapping("/{caseId}/audit-trail")
    @Operation(summary = "Get complete audit trail for a case including AI logs")
    public ResponseEntity<Map<String, Object>> getAuditTrail(
        @PathVariable Long caseId,
        @RequestParam(defaultValue = "0") int page,
        @RequestParam(defaultValue = "20") int size
    ) {
        log.info("Getting audit trail for case: {}", caseId);
        
        Pageable pageable = PageRequest.of(page, size);
        Page<CaseAuditLogDTO> auditLogs = auditLogService.getAuditLogsByCase(caseId, pageable);
        
        Map<String, Object> response = new HashMap<>();
        response.put("status", "success");
        response.put("data", auditLogs.getContent());
        response.put("total", auditLogs.getTotalElements());
        response.put("page", page);
        response.put("size", size);
        response.put("totalPages", auditLogs.getTotalPages());
        
        return ResponseEntity.ok(response);
    }
    
    @GetMapping("/{caseId}/audit-logs")
    @Operation(summary = "Get all audit logs for a case")
    public ResponseEntity<Map<String, Object>> getAuditLogs(@PathVariable Long caseId) {
        log.info("Getting all audit logs for case: {}", caseId);
        
        List<CaseAuditLogDTO> auditLogs = auditLogService.getAuditLogsByCase(caseId);
        
        Map<String, Object> response = new HashMap<>();
        response.put("status", "success");
        response.put("data", auditLogs);
        response.put("total", auditLogs.size());
        
        return ResponseEntity.ok(response);
    }
    
    @GetMapping("/{caseId}/execution-chain")
    @Operation(summary = "Get complete execution chain with AI logs and audit logs")
    public ResponseEntity<Map<String, Object>> getExecutionChain(@PathVariable Long caseId) {
        log.info("Getting execution chain for case: {}", caseId);
        
        Map<String, Object> executionChain = auditLogService.getExecutionChain(caseId);
        
        Map<String, Object> response = new HashMap<>();
        response.put("status", "success");
        response.put("data", executionChain);
        
        return ResponseEntity.ok(response);
    }
}
