package com.riskcontrol.repository;

import com.riskcontrol.entity.AIDecisionRecord;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface AIDecisionRecordRepository extends JpaRepository<AIDecisionRecord, Long> {
    
    /**
     * Find the latest AI decision by case ID.
     */
    Optional<AIDecisionRecord> findTopByCaseIdAndDeletedAtIsNullOrderByCreatedAtDesc(Long caseId);
    
    /**
     * Find AI decisions by prompt version
     */
    Page<AIDecisionRecord> findByPromptVersion(String promptVersion, Pageable pageable);
    
    /**
     * Find AI decisions by suggested action
     */
    @Query("SELECT a FROM AIDecisionRecord a WHERE a.suggestedAction = :suggestedAction")
    Page<AIDecisionRecord> findByAiDecision(@Param("suggestedAction") String suggestedAction, Pageable pageable);
    
    /**
     * Find overridden decisions
     */
    @Query("SELECT a FROM AIDecisionRecord a WHERE a.overrideFlag = true AND a.deletedAt IS NULL")
    Page<AIDecisionRecord> findOverriddenDecisions(Pageable pageable);
    
    /**
     * Find decisions by prompt version and override flag
     */
    @Query("SELECT a FROM AIDecisionRecord a WHERE a.promptVersion = :promptVersion AND a.overrideFlag = :overrideFlag AND a.deletedAt IS NULL")
    Page<AIDecisionRecord> findByPromptVersionAndOverrideFlag(
        @Param("promptVersion") String promptVersion,
        @Param("overrideFlag") Boolean overrideFlag,
        Pageable pageable
    );
    
    /**
     * Count overridden decisions by prompt version
     */
    @Query("SELECT COUNT(a) FROM AIDecisionRecord a WHERE a.promptVersion = :promptVersion AND a.overrideFlag = true AND a.deletedAt IS NULL")
    long countOverriddenByPromptVersion(@Param("promptVersion") String promptVersion);
    
    /**
     * Count total decisions by prompt version
     */
    @Query("SELECT COUNT(a) FROM AIDecisionRecord a WHERE a.promptVersion = :promptVersion AND a.deletedAt IS NULL")
    long countByPromptVersion(@Param("promptVersion") String promptVersion);
    
    /**
     * Calculate average response time by prompt version
     */
    @Query("SELECT AVG(a.totalTimeMs) FROM AIDecisionRecord a WHERE a.promptVersion = :promptVersion AND a.deletedAt IS NULL")
    Double getAverageResponseTimeByPromptVersion(@Param("promptVersion") String promptVersion);
    
    /**
     * Find decisions by case ID list
     */
    List<AIDecisionRecord> findByCaseIdIn(List<Long> caseIds);

    /**
     * Check if decision record already exists for case + prompt version.
     */
    boolean existsByCaseIdAndPromptVersionAndDeletedAtIsNull(Long caseId, String promptVersion);
    
    /**
     * Get review efficiency statistics
     */
    @Query(value = "SELECT AVG(a.total_time_ms), COUNT(a.id), MIN(a.total_time_ms), MAX(a.total_time_ms) " +
           "FROM ai_decision_record a WHERE a.created_at >= :startDate AND a.created_at <= :endDate AND a.deleted_at IS NULL",
           nativeQuery = true)
    List<Object[]> getReviewEfficiencyStats(
        @Param("startDate") java.time.LocalDateTime startDate,
        @Param("endDate") java.time.LocalDateTime endDate
    );
    
    /**
     * Get override rate statistics
     */
    @Query(value = "SELECT COUNT(a.id), SUM(CASE WHEN a.override_flag = true THEN 1 ELSE 0 END) " +
           "FROM ai_decision_record a WHERE a.created_at >= :startDate AND a.created_at <= :endDate AND a.deleted_at IS NULL",
           nativeQuery = true)
    List<Object[]> getOverrideRateStats(
        @Param("startDate") java.time.LocalDateTime startDate,
        @Param("endDate") java.time.LocalDateTime endDate
    );
    
    /**
     * Get override rate by prompt version
     */
    @Query(value = "SELECT a.prompt_version, COUNT(a.id), SUM(CASE WHEN a.override_flag = true THEN 1 ELSE 0 END) " +
           "FROM ai_decision_record a WHERE a.created_at >= :startDate AND a.created_at <= :endDate AND a.deleted_at IS NULL " +
           "GROUP BY a.prompt_version",
           nativeQuery = true)
    List<Object[]> getOverrideRateByVersion(
        @Param("startDate") java.time.LocalDateTime startDate,
        @Param("endDate") java.time.LocalDateTime endDate
    );
    
    /**
     * Get prompt version comparison
     */
    @Query(value = "SELECT a.prompt_version, COUNT(a.id), " +
           "COALESCE(SUM(CASE WHEN a.suggested_action = 'APPROVE' THEN 1 ELSE 0 END), 0), " +
           "COALESCE(SUM(CASE WHEN a.suggested_action = 'REJECT' THEN 1 ELSE 0 END), 0), " +
           "COALESCE(SUM(CASE WHEN a.override_flag = true THEN 1 ELSE 0 END), 0), " +
           "COALESCE(AVG(a.total_time_ms), 0) " +
           "FROM ai_decision_record a WHERE a.created_at >= :startDate AND a.created_at <= :endDate AND a.deleted_at IS NULL " +
           "GROUP BY a.prompt_version ORDER BY a.prompt_version",
           nativeQuery = true)
    List<Object[]> getPromptVersionComparison(
        @Param("startDate") java.time.LocalDateTime startDate,
        @Param("endDate") java.time.LocalDateTime endDate
    );
    
    /**
     * Get review efficiency trend
     */
    @Query(value = "SELECT DATE(a.created_at), AVG(a.total_time_ms), COUNT(a.id) " +
           "FROM ai_decision_record a WHERE a.created_at >= :startDate AND a.created_at <= :endDate AND a.deleted_at IS NULL " +
           "GROUP BY DATE(a.created_at) ORDER BY DATE(a.created_at)",
           nativeQuery = true)
    List<Object[]> getReviewEfficiencyTrend(
        @Param("startDate") java.time.LocalDateTime startDate,
        @Param("endDate") java.time.LocalDateTime endDate
    );
    
    /**
     * Get override rate trend
     */
    @Query(value = "SELECT DATE(a.created_at), COUNT(a.id), SUM(CASE WHEN a.override_flag = true THEN 1 ELSE 0 END) " +
           "FROM ai_decision_record a WHERE a.created_at >= :startDate AND a.created_at <= :endDate AND a.deleted_at IS NULL " +
           "GROUP BY DATE(a.created_at) ORDER BY DATE(a.created_at)",
           nativeQuery = true)
    List<Object[]> getOverrideRateTrend(
        @Param("startDate") java.time.LocalDateTime startDate,
        @Param("endDate") java.time.LocalDateTime endDate
    );
}
