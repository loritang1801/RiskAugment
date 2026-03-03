package com.riskcontrol.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.riskcontrol.dto.UserDTO;
import com.riskcontrol.dto.request.CreateUserRequest;
import com.riskcontrol.dto.request.UpdateUserRequest;
import com.riskcontrol.exception.ResourceNotFoundException;
import com.riskcontrol.service.UserService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageImpl;
import org.springframework.http.MediaType;
import org.springframework.security.test.context.support.WithMockUser;
import org.springframework.test.web.servlet.MockMvc;

import java.time.LocalDateTime;
import java.util.List;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.put;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest
@ActiveProfiles("test")
@AutoConfigureMockMvc
@WithMockUser(username = "admin", roles = {"ADMIN"})
class UserControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @MockBean
    private UserService userService;

    private UserDTO userDTO;

    @BeforeEach
    void setUp() {
        userDTO = UserDTO.builder()
            .id(1L)
            .username("test_admin")
            .email("test_admin@example.com")
            .fullName("Test Admin")
            .role("ADMIN")
            .department("Risk")
            .status("ACTIVE")
            .createdAt(LocalDateTime.now())
            .updatedAt(LocalDateTime.now())
            .build();
    }

    @Test
    void testCreateUser_Success() throws Exception {
        CreateUserRequest request = CreateUserRequest.builder()
            .username("test_admin")
            .email("test_admin@example.com")
            .password("Password123")
            .fullName("Test Admin")
            .role("ADMIN")
            .department("Risk")
            .build();

        when(userService.createUser(any(CreateUserRequest.class))).thenReturn(userDTO);

        mockMvc.perform(post("/api/users")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(request)))
            .andExpect(status().isCreated())
            .andExpect(jsonPath("$.status").value("success"))
            .andExpect(jsonPath("$.data.id").value(1L))
            .andExpect(jsonPath("$.timestamp").exists())
            .andExpect(jsonPath("$.traceId").exists());
    }

    @Test
    void testListUsers_Success() throws Exception {
        Page<UserDTO> page = new PageImpl<>(List.of(userDTO));
        when(userService.listUsers(0, 10)).thenReturn(page);

        mockMvc.perform(get("/api/users?page=0&size=10"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.status").value("success"))
            .andExpect(jsonPath("$.data[0].username").value("test_admin"))
            .andExpect(jsonPath("$.timestamp").exists())
            .andExpect(jsonPath("$.traceId").exists());
    }

    @Test
    void testUpdateUser_Success() throws Exception {
        UpdateUserRequest request = UpdateUserRequest.builder()
            .fullName("Updated Admin")
            .role("REVIEWER")
            .department("Fraud")
            .status("INACTIVE")
            .build();

        UserDTO updated = UserDTO.builder()
            .id(1L)
            .username("test_admin")
            .email("test_admin@example.com")
            .fullName("Updated Admin")
            .role("REVIEWER")
            .department("Fraud")
            .status("INACTIVE")
            .build();

        when(userService.updateUser(eq(1L), any(UpdateUserRequest.class))).thenReturn(updated);

        mockMvc.perform(put("/api/users/1")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(request)))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.status").value("success"))
            .andExpect(jsonPath("$.data.role").value("REVIEWER"))
            .andExpect(jsonPath("$.timestamp").exists())
            .andExpect(jsonPath("$.traceId").exists());
    }

    @Test
    void testGetUserById_NotFound() throws Exception {
        when(userService.getUserById(999L)).thenThrow(new ResourceNotFoundException("User not found with ID: 999"));

        mockMvc.perform(get("/api/users/999"))
            .andExpect(status().isNotFound())
            .andExpect(jsonPath("$.status").value("error"))
            .andExpect(jsonPath("$.code").value("NOT_FOUND"))
            .andExpect(jsonPath("$.message").value("User not found with ID: 999"))
            .andExpect(jsonPath("$.timestamp").exists())
            .andExpect(jsonPath("$.traceId").exists());
    }
}
