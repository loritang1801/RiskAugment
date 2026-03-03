package com.riskcontrol.repository;

import com.riskcontrol.entity.PromptTemplate;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

/**
 * Repository for PromptTemplate entity.
 */
@Repository
public interface PromptTemplateRepository extends JpaRepository<PromptTemplate, Long> {
    
    /**
     * Find prompt template by version.
     */
    Optional<PromptTemplate> findByVersion(String version);
    
    /**
     * Find active prompt template.
     */
    Optional<PromptTemplate> findByIsActiveTrue();
    
    /**
     * Find all prompt templates ordered by creation date.
     */
    List<PromptTemplate> findAllByOrderByCreatedAtDesc();
    
    /**
     * Check if version exists.
     */
    boolean existsByVersion(String version);
}
