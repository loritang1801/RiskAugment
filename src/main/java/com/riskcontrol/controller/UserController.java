package com.riskcontrol.controller;

import com.riskcontrol.dto.UserDTO;
import com.riskcontrol.dto.request.CreateUserRequest;
import com.riskcontrol.dto.request.UpdateUserRequest;
import com.riskcontrol.service.UserService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@Slf4j
@RestController
@RequestMapping("/api/users")
@RequiredArgsConstructor
@Tag(name = "User Management", description = "APIs for user management")
public class UserController {
    
    private final UserService userService;
    
    @PostMapping
    @Operation(summary = "Create a new user")
    public ResponseEntity<Map<String, Object>> createUser(@Valid @RequestBody CreateUserRequest request) {
        log.info("Creating user: {}", request.getUsername());
        
        UserDTO userDTO = userService.createUser(request);
        
        Map<String, Object> response = new HashMap<>();
        response.put("status", "success");
        response.put("data", userDTO);
        
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }
    
    @GetMapping("/{id}")
    @Operation(summary = "Get user by ID")
    public ResponseEntity<Map<String, Object>> getUserById(@PathVariable Long id) {
        log.info("Getting user: {}", id);
        
        UserDTO userDTO = userService.getUserById(id);
        
        Map<String, Object> response = new HashMap<>();
        response.put("status", "success");
        response.put("data", userDTO);
        
        return ResponseEntity.ok(response);
    }
    
    @GetMapping("/username/{username}")
    @Operation(summary = "Get user by username")
    public ResponseEntity<Map<String, Object>> getUserByUsername(@PathVariable String username) {
        log.info("Getting user by username: {}", username);
        
        UserDTO userDTO = userService.getUserByUsername(username);
        
        Map<String, Object> response = new HashMap<>();
        response.put("status", "success");
        response.put("data", userDTO);
        
        return ResponseEntity.ok(response);
    }
    
    @GetMapping
    @Operation(summary = "List all users")
    public ResponseEntity<Map<String, Object>> listUsers(
        @RequestParam(defaultValue = "0") int page,
        @RequestParam(defaultValue = "20") int size
    ) {
        log.info("Listing users - page: {}, size: {}", page, size);
        
        Page<UserDTO> users = userService.listUsers(page, size);
        
        Map<String, Object> response = new HashMap<>();
        response.put("status", "success");
        response.put("data", users.getContent());
        response.put("total", users.getTotalElements());
        response.put("page", page);
        response.put("size", size);
        response.put("totalPages", users.getTotalPages());
        
        return ResponseEntity.ok(response);
    }
    
    @GetMapping("/role/{role}")
    @Operation(summary = "List users by role")
    public ResponseEntity<Map<String, Object>> listUsersByRole(
        @PathVariable String role,
        @RequestParam(defaultValue = "0") int page,
        @RequestParam(defaultValue = "20") int size
    ) {
        log.info("Listing users by role: {} - page: {}, size: {}", role, page, size);
        
        Page<UserDTO> users = userService.listUsersByRole(role, page, size);
        
        Map<String, Object> response = new HashMap<>();
        response.put("status", "success");
        response.put("data", users.getContent());
        response.put("total", users.getTotalElements());
        response.put("page", page);
        response.put("size", size);
        response.put("totalPages", users.getTotalPages());
        
        return ResponseEntity.ok(response);
    }
    
    @PutMapping("/{id}")
    @Operation(summary = "Update user")
    public ResponseEntity<Map<String, Object>> updateUser(
        @PathVariable Long id,
        @Valid @RequestBody UpdateUserRequest request
    ) {
        log.info("Updating user: {}", id);
        
        UserDTO userDTO = userService.updateUser(id, request);
        
        Map<String, Object> response = new HashMap<>();
        response.put("status", "success");
        response.put("data", userDTO);
        
        return ResponseEntity.ok(response);
    }
    
    @DeleteMapping("/{id}")
    @Operation(summary = "Delete user")
    public ResponseEntity<Map<String, Object>> deleteUser(@PathVariable Long id) {
        log.info("Deleting user: {}", id);
        
        userService.deleteUser(id);
        
        Map<String, Object> response = new HashMap<>();
        response.put("status", "success");
        response.put("message", "User deleted successfully");
        
        return ResponseEntity.ok(response);
    }
    
    @PutMapping("/{id}/deactivate")
    @Operation(summary = "Deactivate user")
    public ResponseEntity<Map<String, Object>> deactivateUser(@PathVariable Long id) {
        log.info("Deactivating user: {}", id);
        
        UserDTO userDTO = userService.deactivateUser(id);
        
        Map<String, Object> response = new HashMap<>();
        response.put("status", "success");
        response.put("data", userDTO);
        
        return ResponseEntity.ok(response);
    }
}
