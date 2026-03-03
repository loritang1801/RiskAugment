package com.riskcontrol.repository;

import com.riskcontrol.entity.User;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    
    /**
     * Find user by username
     */
    Optional<User> findByUsername(String username);
    
    /**
     * Find user by email
     */
    Optional<User> findByEmail(String email);
    
    /**
     * Find users by role
     */
    Page<User> findByRole(String role, Pageable pageable);
    
    /**
     * Find users by status
     */
    Page<User> findByStatus(String status, Pageable pageable);
    
    /**
     * Find active users
     */
    @Query("SELECT u FROM User u WHERE u.status = 'ACTIVE' AND u.deletedAt IS NULL")
    Page<User> findActiveUsers(Pageable pageable);

    /**
     * Find user full name by ID.
     */
    @Query("SELECT u.fullName FROM User u WHERE u.id = :id")
    Optional<String> findFullNameById(@Param("id") Long id);
    
    /**
     * Check if username exists
     */
    boolean existsByUsername(String username);
    
    /**
     * Check if email exists
     */
    boolean existsByEmail(String email);
}
