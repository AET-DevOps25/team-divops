package com.example.gateway.service;

import com.example.gateway.model.Session;
import com.example.gateway.repository.SessionRepository;
import com.example.gateway.client.UserServiceClient;

import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.*;

import lombok.RequiredArgsConstructor;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
@Transactional
public class AuthService {

    private final JwtService jwt;
    private final SessionRepository sessions;
    private final UserServiceClient users;

    private Map<String, String> issueTokens(String email) {
        var access = jwt.generate(email);
        var refresh = UUID.randomUUID().toString();
        sessions.deleteByEmail(email);
        sessions.save(new Session(email, refresh, Instant.now().plus(7, ChronoUnit.DAYS)));
        return Map.of("accessToken", access, "refreshToken", refresh);
    }

    public Map<String, String> signUp(Map<String, String> dto) {
        users.register(dto);
        return issueTokens(dto.get("email"));
    }

    public Map<String, String> signIn(String email, String pwd) {
        if (!users.verify(email, pwd)) throw new BadCredentialsException("Bad credentials");
        return issueTokens(email);
    }

    public Map<String, String> refresh(String refreshToken) {
        var s = sessions.findByRefreshToken(refreshToken)
                .filter(sess -> sess.getExpiresAt().isAfter(Instant.now()))
                .orElseThrow(() -> new BadCredentialsException("Refresh invalid"));
        return Map.of("accessToken", jwt.generate(s.getEmail()));
    }
}
