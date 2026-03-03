package com.riskcontrol.service;

import com.riskcontrol.dto.UserDTO;
import com.riskcontrol.dto.request.CreateUserRequest;
import com.riskcontrol.dto.request.UpdateUserRequest;
import com.riskcontrol.entity.User;
import com.riskcontrol.exception.ResourceNotFoundException;
import com.riskcontrol.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Slf4j
@Service
@RequiredArgsConstructor
public class UserService {
    
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    
    /**
     * Create a new user
     */
    @Transactional
    public UserDTO createUser(CreateUserRequest request) {
        log.info("Creating user: {}", request.getUsername());
        
        // Check if username already exists
        if (userRepository.existsByUsername(request.getUsername())) {
            throw new IllegalArgumentException("Username already exists");
        }
        
        // Check if email already exists
        if (userRepository.existsByEmail(request.getEmail())) {
            throw new IllegalArgumentException("Email already exists");
        }
        
        // Create new user
        User user = User.builder()
            .username(request.getUsername())
            .email(request.getEmail())
            .passwordHash(passwordEncoder.encode(request.getPassword()))
            .fullName(request.getFullName())
            .role(request.getRole())
            .department(request.getDepartment())
            .status("ACTIVE")
            .build();
        
        User savedUser = userRepository.save(user);
        log.info("User created successfully: {}", savedUser.getId());
        
        return UserDTO.from(savedUser);
    }
    
    /**
     * Get user by ID
     */
    public UserDTO getUserById(Long id) {
        log.debug("Getting user by ID: {}", id);
        
        User user = userRepository.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("User not found with ID: " + id));
        
        return UserDTO.from(user);
    }
    
    /**
     * Get user by username
     */
    public UserDTO getUserByUsername(String username) {
        log.debug("Getting user by username: {}", username);
        
        User user = userRepository.findByUsername(username)
            .orElseThrow(() -> new ResourceNotFoundException("User not found with username: " + username));
        
        return UserDTO.from(user);
    }
    
    /**
     * List all users with pagination
     */
    public Page<UserDTO> listUsers(int page, int size) {
        log.debug("Listing users - page: {}, size: {}", page, size);
        
        Pageable pageable = PageRequest.of(page, size);
        return userRepository.findAll(pageable).map(UserDTO::from);
    }
    
    /**
     * List users by role
     */
    public Page<UserDTO> listUsersByRole(String role, int page, int size) {
        log.debug("Listing users by role: {} - page: {}, size: {}", role, page, size);
        
        Pageable pageable = PageRequest.of(page, size);
        return userRepository.findByRole(role, pageable).map(UserDTO::from);
    }
    
    /**
     * Update user
     */
    @Transactional
    public UserDTO updateUser(Long id, UpdateUserRequest request) {
        log.info("Updating user: {}", id);
        
        User user = userRepository.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("User not found with ID: " + id));
        
        user.setFullName(request.getFullName());
        user.setDepartment(request.getDepartment());
        user.setRole(request.getRole());
        if (request.getStatus() != null && !request.getStatus().isBlank()) {
            user.setStatus(request.getStatus());
        }
        
        User updatedUser = userRepository.save(user);
        log.info("User updated successfully: {}", id);
        
        return UserDTO.from(updatedUser);
    }
    
    /**
     * Delete user
     */
    @Transactional
    public void deleteUser(Long id) {
        log.info("Deleting user: {}", id);
        
        User user = userRepository.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("User not found with ID: " + id));

        String currentUsername = getCurrentUsername();
        if (currentUsername != null && currentUsername.equals(user.getUsername())) {
            throw new IllegalArgumentException("You cannot delete your own account");
        }
        
        userRepository.delete(user);
        log.info("User deleted successfully: {}", id);
    }
    
    /**
     * Deactivate user
     */
    @Transactional
    public UserDTO deactivateUser(Long id) {
        log.info("Deactivating user: {}", id);
        
        User user = userRepository.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("User not found with ID: " + id));

        String currentUsername = getCurrentUsername();
        if (currentUsername != null && currentUsername.equals(user.getUsername())) {
            throw new IllegalArgumentException("You cannot deactivate your own account");
        }
        
        user.setStatus("INACTIVE");
        User updatedUser = userRepository.save(user);
        log.info("User deactivated successfully: {}", id);
        
        return UserDTO.from(updatedUser);
    }

    private String getCurrentUsername() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null) {
            return null;
        }
        return authentication.getName();
    }
}
