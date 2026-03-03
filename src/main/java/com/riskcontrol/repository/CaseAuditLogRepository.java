package com.riskcontrol.repository;

import com.riskcontrol.entity.CaseAuditLog;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

/**
 * Repository for CaseAuditLog entity.
 */
@Repository
public interface CaseAuditLogRepository extends JpaRepository<CaseAuditLog, Long> {
    
    /**
     * Find audit logs by case ID.
     */
    List<CaseAuditLog> findByCaseIdOrderByCreatedAtDesc(Long caseId);
    
    /**
     * Find audit logs by case ID with pagination.
     */
    Page<CaseAuditLog> findByCaseIdOrderByCreatedAtDesc(Long caseId, Pageable pageable);
    
    /**
     * Find audit logs by operation type.
     */
    List<CaseAuditLog> findByOperationOrderByCreatedAtDesc(String operation);
    
    /**
     * Find audit logs by operator ID.
     */
    List<CaseAuditLog> findByOperatorIdOrderByCreatedAtDesc(Long operatorId);
    
    /**
     * Find audit logs within date range.
     */
    @Query("SELECT a FROM CaseAuditLog a WHERE a.createdAt BETWEEN :startDate AND :endDate ORDER BY a.createdAt DESC")
    List<CaseAuditLog> findByDateRange(@Param("startDate") LocalDateTime startDate, @Param("endDate") LocalDateTime endDate);
    
    /**
     * Find audit logs by case ID and operation type.
     */
    List<CaseAuditLog> findByCaseIdAndOperationOrderByCreatedAtDesc(Long caseId, String operation);
}
