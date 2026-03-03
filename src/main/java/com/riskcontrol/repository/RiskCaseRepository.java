package com.riskcontrol.repository;

import com.riskcontrol.entity.RiskCase;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface RiskCaseRepository extends JpaRepository<RiskCase, Long> {
    
    /**
     * Find case by business transaction ID
     */
    Optional<RiskCase> findByBizTransactionId(String bizTransactionId);
    
    /**
     * Find cases by status
     */
    Page<RiskCase> findByRiskStatus(String riskStatus, Pageable pageable);
    
    /**
     * Find cases by risk level
     */
    Page<RiskCase> findByRiskLevel(String riskLevel, Pageable pageable);
    
    /**
     * Find cases by country
     */
    Page<RiskCase> findByCountry(String country, Pageable pageable);
    
    /**
     * Find cases by device risk
     */
    Page<RiskCase> findByDeviceRisk(String deviceRisk, Pageable pageable);
    
    /**
     * Find cases by reviewer
     */
    Page<RiskCase> findByReviewerId(Long reviewerId, Pageable pageable);
    
    /**
     * Find cases by status and risk level
     */
    @Query("SELECT c FROM RiskCase c WHERE c.riskStatus = :status AND c.riskLevel = :riskLevel AND c.deletedAt IS NULL")
    Page<RiskCase> findByStatusAndRiskLevel(
        @Param("status") String status,
        @Param("riskLevel") String riskLevel,
        Pageable pageable
    );
    
    /**
     * Find cases by country and risk level
     */
    @Query("SELECT c FROM RiskCase c WHERE c.country = :country AND c.riskLevel = :riskLevel AND c.deletedAt IS NULL")
    Page<RiskCase> findByCountryAndRiskLevel(
        @Param("country") String country,
        @Param("riskLevel") String riskLevel,
        Pageable pageable
    );
    
    /**
     * Find pending cases
     */
    @Query("SELECT c FROM RiskCase c WHERE c.riskStatus = 'PENDING' AND c.deletedAt IS NULL ORDER BY c.createdAt DESC")
    Page<RiskCase> findPendingCases(Pageable pageable);
    
    /**
     * Count cases by status
     */
    long countByRiskStatus(String riskStatus);
    
    /**
     * Count cases by risk level
     */
    long countByRiskLevel(String riskLevel);
    
    /**
     * Find cases by multiple criteria
     */
    @Query("SELECT c FROM RiskCase c WHERE " +
           "(:bizTransactionId IS NULL OR c.bizTransactionId LIKE %:bizTransactionId%) AND " +
           "(:status IS NULL OR c.riskStatus = :status) AND " +
           "(:riskLevel IS NULL OR c.riskLevel = :riskLevel) AND " +
           "(:country IS NULL OR c.country = :country) AND " +
           "c.deletedAt IS NULL")
    Page<RiskCase> findByCriteria(
        @Param("bizTransactionId") String bizTransactionId,
        @Param("status") String status,
        @Param("riskLevel") String riskLevel,
        @Param("country") String country,
        Pageable pageable
    );
}
