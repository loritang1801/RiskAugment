package com.riskcontrol.service;

import com.riskcontrol.dto.RiskCaseDTO;
import com.riskcontrol.dto.request.CreateRiskCaseRequest;
import com.riskcontrol.entity.RiskCase;
import com.riskcontrol.entity.User;
import com.riskcontrol.exception.ResourceNotFoundException;
import com.riskcontrol.repository.AIDecisionRecordRepository;
import com.riskcontrol.repository.RiskCaseRepository;
import com.riskcontrol.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Slf4j
@Service
@RequiredArgsConstructor
public class RiskCaseService {
    
    private final RiskCaseRepository riskCaseRepository;
    private final CaseAuditLogService caseAuditLogService;
    private final AIDecisionRecordRepository aiDecisionRecordRepository;
    private final UserRepository userRepository;
    
    /**
     * Create a new risk case
     */
    @Transactional
    public RiskCaseDTO createRiskCase(CreateRiskCaseRequest request) {
        log.info("Creating risk case: {}", request.getBizTransactionId());
        
        // Check if transaction ID already exists
        if (riskCaseRepository.findByBizTransactionId(request.getBizTransactionId()).isPresent()) {
            throw new IllegalArgumentException("Risk case with this transaction ID already exists");
        }
        
        // Create new risk case
        RiskCase riskCase = RiskCase.builder()
            .bizTransactionId(request.getBizTransactionId())
            .amount(request.getAmount())
            .currency(request.getCurrency())
            .country(request.getCountry())
            .deviceRisk(request.getDeviceRisk())
            .userLabel(request.getUserLabel())
            .riskFeatures(request.getRiskFeatures())
            .ruleEngineScore(request.getRuleEngineScore())
            .triggeredRules(request.getTriggeredRules())
            .riskScore(request.getRiskScore())
            .riskLevel(request.getRiskLevel())
            .riskStatus(request.getRiskStatus())
            .build();
        
        RiskCase savedCase = riskCaseRepository.save(riskCase);
        
        // Log CREATE operation
        caseAuditLogService.logOperation(savedCase.getId(), null, "CREATE", null, RiskCaseDTO.from(savedCase));
        
        log.info("Risk case created successfully: {}", savedCase.getId());
        
        return RiskCaseDTO.from(savedCase);
    }
    
    /**
     * Get risk case by ID
     */
    public RiskCaseDTO getRiskCaseById(Long id) {
        log.debug("Getting risk case by ID: {}", id);
        
        RiskCase riskCase = riskCaseRepository.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("Risk case not found with ID: " + id));
        
        return RiskCaseDTO.from(riskCase);
    }
    
    /**
     * Get risk case by business transaction ID
     */
    public RiskCaseDTO getRiskCaseByBizTransactionId(String bizTransactionId) {
        log.debug("Getting risk case by transaction ID: {}", bizTransactionId);
        
        RiskCase riskCase = riskCaseRepository.findByBizTransactionId(bizTransactionId)
            .orElseThrow(() -> new ResourceNotFoundException("Risk case not found with transaction ID: " + bizTransactionId));
        
        return RiskCaseDTO.from(riskCase);
    }
    
    /**
     * List all risk cases with pagination
     */
    public Page<RiskCaseDTO> listRiskCases(int page, int size) {
        log.debug("Listing risk cases - page: {}, size: {}", page, size);
        
        Pageable pageable = PageRequest.of(page, size);
        return riskCaseRepository.findAll(pageable).map(RiskCaseDTO::from);
    }
    
    /**
     * List risk cases by status
     */
    public Page<RiskCaseDTO> listRiskCasesByStatus(String status, int page, int size) {
        log.debug("Listing risk cases by status: {} - page: {}, size: {}", status, page, size);
        
        Pageable pageable = PageRequest.of(page, size);
        return riskCaseRepository.findByRiskStatus(status, pageable).map(RiskCaseDTO::from);
    }
    
    /**
     * List risk cases by risk level
     */
    public Page<RiskCaseDTO> listRiskCasesByRiskLevel(String riskLevel, int page, int size) {
        log.debug("Listing risk cases by risk level: {} - page: {}, size: {}", riskLevel, page, size);
        
        Pageable pageable = PageRequest.of(page, size);
        return riskCaseRepository.findByRiskLevel(riskLevel, pageable).map(RiskCaseDTO::from);
    }
    
    /**
     * List pending risk cases
     */
    public Page<RiskCaseDTO> listPendingRiskCases(int page, int size) {
        log.debug("Listing pending risk cases - page: {}, size: {}", page, size);
        
        Pageable pageable = PageRequest.of(page, size);
        return riskCaseRepository.findPendingCases(pageable).map(RiskCaseDTO::from);
    }
    
    /**
     * Search risk cases by multiple criteria
     */
    public Page<RiskCaseDTO> searchRiskCases(String bizTransactionId, String status, String riskLevel, String country, int page, int size) {
        log.debug("Searching risk cases - bizTransactionId: {}, status: {}, riskLevel: {}, country: {}, page: {}, size: {}", 
            bizTransactionId, status, riskLevel, country, page, size);
        
        Pageable pageable = PageRequest.of(page, size);
        
        // Convert empty strings to null for optional parameters
        String txnId = (bizTransactionId == null || bizTransactionId.isEmpty()) ? null : bizTransactionId;
        String st = (status == null || status.isEmpty()) ? null : status;
        String rl = (riskLevel == null || riskLevel.isEmpty()) ? null : riskLevel;
        String c = (country == null || country.isEmpty()) ? null : country;
        
        return riskCaseRepository.findByCriteria(txnId, st, rl, c, pageable).map(RiskCaseDTO::from);
    }
    
    /**
     * Update risk case
     */
    @Transactional
    public RiskCaseDTO updateRiskCase(Long id, CreateRiskCaseRequest request) {
        log.info("Updating risk case: {}", id);
        
        RiskCase riskCase = riskCaseRepository.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("Risk case not found with ID: " + id));
        
        RiskCaseDTO oldValue = RiskCaseDTO.from(riskCase);
        
        riskCase.setRiskLevel(request.getRiskLevel());
        riskCase.setRiskScore(request.getRiskScore());
        riskCase.setRuleEngineScore(request.getRuleEngineScore());
        riskCase.setTriggeredRules(request.getTriggeredRules());
        
        RiskCase updatedCase = riskCaseRepository.save(riskCase);
        
        // Log UPDATE operation
        caseAuditLogService.logOperation(id, null, "UPDATE", oldValue, RiskCaseDTO.from(updatedCase));
        
        log.info("Risk case updated successfully: {}", id);
        
        return RiskCaseDTO.from(updatedCase);
    }
    
    /**
     * Update risk case status
     */
    @Transactional
    public RiskCaseDTO updateRiskCaseStatus(Long id, String status) {
        log.info("Updating risk case status: {} -> {}", id, status);
        
        RiskCase riskCase = riskCaseRepository.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("Risk case not found with ID: " + id));
        
        RiskCaseDTO oldValue = RiskCaseDTO.from(riskCase);
        
        riskCase.setRiskStatus(status);
        RiskCase updatedCase = riskCaseRepository.save(riskCase);
        
        // Log STATUS_UPDATE operation
        caseAuditLogService.logOperation(id, null, "STATUS_UPDATE", oldValue, RiskCaseDTO.from(updatedCase));
        
        log.info("Risk case status updated successfully: {}", id);
        
        return RiskCaseDTO.from(updatedCase);
    }
    
    /**
     * Approve risk case
     */
    @Transactional
    public RiskCaseDTO approveRiskCase(Long id, String reviewerUsername) {
        if (reviewerUsername == null || reviewerUsername.isBlank()) {
            throw new IllegalArgumentException("Reviewer username is required");
        }
        User reviewer = userRepository.findByUsername(reviewerUsername)
            .orElseThrow(() -> new ResourceNotFoundException("Reviewer not found: " + reviewerUsername));
        Long reviewerId = reviewer.getId();
        log.info("Approving risk case: {} by reviewer: {} ({})", id, reviewerId, reviewerUsername);
        
        RiskCase riskCase = riskCaseRepository.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("Risk case not found with ID: " + id));
        
        RiskCaseDTO oldValue = RiskCaseDTO.from(riskCase);
        
        riskCase.setRiskStatus("APPROVED");
        riskCase.setFinalDecision("APPROVE");
        riskCase.setReviewerId(reviewerId);
        
        // Check if this is an override (AI suggested REJECT but reviewer approved)
        var aiDecision = aiDecisionRecordRepository.findTopByCaseIdAndDeletedAtIsNullOrderByCreatedAtDesc(id);
        if (aiDecision.isPresent() && "REJECT".equals(aiDecision.get().getSuggestedAction())) {
            aiDecision.get().setOverrideFlag(true);
            aiDecisionRecordRepository.save(aiDecision.get());
            log.info("Override detected: AI suggested REJECT but reviewer approved");
        }
        
        RiskCase updatedCase = riskCaseRepository.save(riskCase);
        
        // Log APPROVE operation
        caseAuditLogService.logOperation(id, reviewerId, "APPROVE", oldValue, RiskCaseDTO.from(updatedCase));
        
        log.info("Risk case approved successfully: {}", id);
        
        return RiskCaseDTO.from(updatedCase);
    }
    
    /**
     * Reject risk case
     */
    @Transactional
    public RiskCaseDTO rejectRiskCase(Long id, String reviewerUsername) {
        if (reviewerUsername == null || reviewerUsername.isBlank()) {
            throw new IllegalArgumentException("Reviewer username is required");
        }
        User reviewer = userRepository.findByUsername(reviewerUsername)
            .orElseThrow(() -> new ResourceNotFoundException("Reviewer not found: " + reviewerUsername));
        Long reviewerId = reviewer.getId();
        log.info("Rejecting risk case: {} by reviewer: {} ({})", id, reviewerId, reviewerUsername);
        
        RiskCase riskCase = riskCaseRepository.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("Risk case not found with ID: " + id));
        
        RiskCaseDTO oldValue = RiskCaseDTO.from(riskCase);
        
        riskCase.setRiskStatus("REJECTED");
        riskCase.setFinalDecision("REJECT");
        riskCase.setReviewerId(reviewerId);
        
        // Check if this is an override (AI suggested APPROVE but reviewer rejected)
        var aiDecision = aiDecisionRecordRepository.findTopByCaseIdAndDeletedAtIsNullOrderByCreatedAtDesc(id);
        if (aiDecision.isPresent() && "APPROVE".equals(aiDecision.get().getSuggestedAction())) {
            aiDecision.get().setOverrideFlag(true);
            aiDecisionRecordRepository.save(aiDecision.get());
            log.info("Override detected: AI suggested APPROVE but reviewer rejected");
        }
        
        RiskCase updatedCase = riskCaseRepository.save(riskCase);
        
        // Log REJECT operation
        caseAuditLogService.logOperation(id, reviewerId, "REJECT", oldValue, RiskCaseDTO.from(updatedCase));
        
        log.info("Risk case rejected successfully: {}", id);
        
        return RiskCaseDTO.from(updatedCase);
    }
    
    /**
     * Delete risk case
     */
    @Transactional
    public void deleteRiskCase(Long id) {
        log.info("Deleting risk case: {}", id);
        
        RiskCase riskCase = riskCaseRepository.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("Risk case not found with ID: " + id));
        
        riskCaseRepository.delete(riskCase);
        log.info("Risk case deleted successfully: {}", id);
    }
}
