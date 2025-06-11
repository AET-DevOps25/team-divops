package com.example.gateway.controller;

import com.example.gateway.client.UserServiceClient;
import com.example.gateway.service.AuthService;
import io.swagger.v3.oas.annotations.Operation;

import java.util.*;

import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/auth")
@RequiredArgsConstructor
public class AuthController {

    private final AuthService auth;
    private final UserServiceClient users;

    /* ───────── PUBLIC ───────── */
    @Operation(summary = "Sign up new user",
            security = @SecurityRequirement(name = "BasicAuth"))
    @PostMapping("/signup")
    public Map<String, String> signup(@RequestBody Map<String, String> dto) {
        return auth.signUp(dto);
    }

    @Operation(summary = "Sign in (Basic → tokens)",
            security = @SecurityRequirement(name = "BasicAuth"))
    @PostMapping("/signin")
    public Map<String, String> signin(@RequestHeader("Authorization") String basicHdr) {
        var plain = new String(Base64.getDecoder().decode(basicHdr.substring(6)));
        String[] parts = plain.split(":", 2);
        return auth.signIn(parts[0], parts[1]);
    }

    @Operation(summary = "Refresh access token",            // no auth needed
            security = {})
    @PostMapping("/refresh-token")
    public Map<String, String> refresh(@RequestBody Map<String, String> body) {
        return auth.refresh(body.get("refreshToken"));
    }

    /* ───────── JWT-protected ───────── */
    @Operation(summary = "Current user info")
    @GetMapping("/me")
    public Map<String, Object> me(Authentication authn) {
        return users.find(authn.getName());
    }
}
