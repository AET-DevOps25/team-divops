package com.example.userservice.controller;

import com.example.userservice.service.UserService;

import java.util.Map;

import io.swagger.v3.oas.annotations.Operation;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

@RestController
@RequestMapping("/internal")
@RequiredArgsConstructor
public class InternalUserController {

    private final UserService users;

    @Operation(summary = "Create user (internal)")
    @PostMapping("/users")
    void create(@RequestBody Map<String, String> dto) {
        users.register(dto);
    }

    @Operation(summary = "Verify credentials (internal)")
    @PostMapping("/auth/verify")
    void verify(@RequestBody Map<String, String> dto) {
        if (!users.verify(dto.get("email"), dto.get("password")))
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED);
    }

    @Operation(summary = "Find user by email (internal)")
    @GetMapping("/users/{email}")
    Map<String, Object> find(@PathVariable String email) {
        return users.find(email);
    }
}
