package com.example.gateway.model;

import jakarta.persistence.*;
import lombok.Getter;
import org.hibernate.annotations.UuidGenerator;

import java.time.Instant;

@Entity
@Table(name = "sessions")
public class Session {
    @Id
    @GeneratedValue
    @UuidGenerator
    @Column(updatable = false, nullable = false)
    private String id;

    @Getter
    @Column(name = "email", nullable = false, unique = true)
    private String email;

    @Column(name = "refresh_token", nullable = false, unique = true)
    private String refreshToken;

    @Getter
    @Column(name = "expires_at", nullable = false)
    private Instant expiresAt;

    protected Session() {
    }

    public Session(String email, String refreshToken, Instant expiresAt) {
        this.email = email;
        this.refreshToken = refreshToken;
        this.expiresAt = expiresAt;
    }
}
