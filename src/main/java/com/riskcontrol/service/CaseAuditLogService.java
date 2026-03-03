package com.riskcontrol.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.riskcontrol.dto.CaseAuditLogDTO;
import com.riskcontrol.entity.CaseAuditLog;
import com.riskcontrol.entity.RiskCase;
import com.riskcontrol.repository.CaseAuditLogRepository;
import com.riskcontrol.repository.RiskCaseRepository;
import com.riskcontrol.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;

/**
 * Service for Case Audit Log management.
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class CaseAuditLogService {
    
    private final CaseAuditLogRepository auditLogRepository;
    private final RiskCaseRepository riskCaseRepository;
    private final UserRepository userRepository;
    private final ObjectMapper objectMapper;
    
    /**
     * Log an operation on a case.
     */
    @Transactional
    public void logOperation(Long caseId, Long operatorId, String operation, Object oldValue, Object newValue) {
        try {
            Map<String, Object> oldMap = oldValue != null ? objectMapper.convertValue(oldValue, Map.class) : null;
            Map<String, Object> newMap = newValue != null ? objectMapper.convertValue(newValue, Map.class) : null;
            recordAuditLog(caseId, operation, operatorId, null, oldMap, newMap);
        } catch (Exception e) {
            log.error("Error logging operation: {}", e.getMessage());
        }
    }
    
    /**
     * Record an audit log entry.
     */
    @Transactional
    public CaseAuditLogDTO recordAuditLog(
        Long caseId,
        String operation,
        Long operatorId,
        String description,
        Map<String, Object> oldValue,
        Map<String, Object> newValue
    ) {
        log.info("Recording audit log for case: {} operation: {}", caseId, operation);
        
        CaseAuditLog auditLog = CaseAuditLog.builder()
            .caseId(caseId)
            .operation(operation)
            .operatorId(operatorId)
            .description(description)
            .oldValue(oldValue != null ? objectMapper.valueToTree(oldValue) : null)
            .newValue(newValue != null ? objectMapper.valueToTree(newValue) : null)
            .build();
        
        auditLog = auditLogRepository.save(auditLog);
        
        return convertToDTO(auditLog);
    }
    
    /**
     * Get audit logs for a case.
     */
    @Transactional(readOnly = true)
    public List<CaseAuditLogDTO> getAuditLogsByCase(Long caseId) {
        log.info("Getting audit logs for case: {}", caseId);
        
        return auditLogRepository.findByCaseIdOrderByCreatedAtDesc(caseId)
            .stream()
            .map(this::convertToDTO)
            .collect(Collectors.toList());
    }
    
    /**
     * Get audit logs for a case with pagination.
     */
    public Page<CaseAuditLogDTO> getAuditLogsByCase(Long caseId, Pageable pageable) {
        log.info("Getting audit logs for case: {} with pagination", caseId);
        
        return auditLogRepository.findByCaseIdOrderByCreatedAtDesc(caseId, pageable)
            .map(this::convertToDTO);
    }
    
    /**
     * Get audit logs by operation type.
     */
    public List<CaseAuditLogDTO> getAuditLogsByOperation(String operation) {
        log.info("Getting audit logs for operation: {}", operation);
        
        return auditLogRepository.findByOperationOrderByCreatedAtDesc(operation)
            .stream()
            .map(this::convertToDTO)
            .collect(Collectors.toList());
    }
    
    /**
     * Get audit logs by operator.
     */
    public List<CaseAuditLogDTO> getAuditLogsByOperator(Long operatorId) {
        log.info("Getting audit logs for operator: {}", operatorId);
        
        return auditLogRepository.findByOperatorIdOrderByCreatedAtDesc(operatorId)
            .stream()
            .map(this::convertToDTO)
            .collect(Collectors.toList());
    }
    
    /**
     * Get audit logs within date range.
     */
    public List<CaseAuditLogDTO> getAuditLogsByDateRange(LocalDateTime startDate, LocalDateTime endDate) {
        log.info("Getting audit logs between {} and {}", startDate, endDate);
        
        return auditLogRepository.findByDateRange(startDate, endDate)
            .stream()
            .map(this::convertToDTO)
            .collect(Collectors.toList());
    }
    
    /**
     * Get audit trail for a case (complete execution chain).
     */
    public List<CaseAuditLogDTO> getAuditTrail(Long caseId) {
        log.info("Getting audit trail for case: {}", caseId);
        
        return getAuditLogsByCase(caseId);
    }
    
    /**
     * Get complete execution chain with audit logs and AI logs.
     */
    @Transactional(readOnly = true)
    public Map<String, Object> getExecutionChain(Long caseId) {
        log.info("Getting execution chain for case: {}", caseId);
        
        Map<String, Object> chain = new HashMap<>();
        
        // Get case info
        RiskCase riskCase = riskCaseRepository.findById(caseId).orElse(null);
        if (riskCase != null) {
            chain.put("case", Map.of(
                "id", riskCase.getId(),
                "bizTransactionId", riskCase.getBizTransactionId(),
                "amount", riskCase.getAmount(),
                "currency", riskCase.getCurrency(),
                "riskLevel", riskCase.getRiskLevel(),
                "riskStatus", riskCase.getRiskStatus(),
                "createdAt", riskCase.getCreatedAt()
            ));
        }
        
        // Get audit logs
        List<CaseAuditLogDTO> auditLogs = getAuditLogsByCase(caseId);
        chain.put("auditLogs", auditLogs);
        
        return chain;
    }
    
    /**
     * Convert entity to DTO.
     */
    private CaseAuditLogDTO convertToDTO(CaseAuditLog auditLog) {
        String operatorName = null;
        if (auditLog.getOperatorId() != null) {
            operatorName = userRepository.findFullNameById(auditLog.getOperatorId()).orElse(null);
        }
        
        return CaseAuditLogDTO.builder()
            .id(auditLog.getId())
            .caseId(auditLog.getCaseId())
            .operatorId(auditLog.getOperatorId())
            .operatorName(operatorName)
            .operation(auditLog.getOperation())
            .description(auditLog.getDescription())
            .oldValue(auditLog.getOldValue() != null ? objectMapper.convertValue(auditLog.getOldValue(), Map.class) : null)
            .newValue(auditLog.getNewValue() != null ? objectMapper.convertValue(auditLog.getNewValue(), Map.class) : null)
            .createdAt(auditLog.getCreatedAt())
            .build();
    }
}
