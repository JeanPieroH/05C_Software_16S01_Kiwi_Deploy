package com.example.hackathon.Auth.domain;

import com.auth0.jwt.JWT;
import com.auth0.jwt.algorithms.Algorithm;
import com.auth0.jwt.exceptions.JWTVerificationException;
import com.example.hackathon.Usuario.domain.UsuarioService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.AuthenticationException;
import org.springframework.security.core.context.SecurityContext;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.stereotype.Service;

import java.util.Date;

@Service
public class JwtService {

    @Value("${jwt.secret}")
    private String secret;

    @Autowired
    private UsuarioService usuarioService;

    public String extractUsername(String token) {
        return JWT.decode(token).getSubject();
    }

    public String extractRole(String token) {
        return JWT.decode(token).getClaim("role").asString();
    }

    public String generateToken(UserDetails data){
        Date now = new Date();
        Date expiration = new Date(now.getTime() + 1000 * 60 * 60 * 24);

        Algorithm algorithm = Algorithm.HMAC256(secret);
        return JWT.create()
                .withSubject(data.getUsername())
                .withClaim("role", data.getAuthorities().toArray()[0].toString())
                .withIssuedAt(now)
                .withExpiresAt(expiration)
                .sign(algorithm);
    }

    public boolean isTokenValid(String token, String userEmail) {

        UserDetails userDetails = usuarioService.userDetailsService().loadUserByUsername(userEmail);

        final String usernameInToken = extractUsername(token);
        if (usernameInToken == null || !usernameInToken.equals(userDetails.getUsername())) {
            return false;
        }
        try {
            // Esto verifica la firma y la expiración
            JWT.require(Algorithm.HMAC256(secret)).build().verify(token);
            return true;
        } catch (JWTVerificationException e) {
            // Loguear el error del token (ej. expirado, firma inválida)
            System.err.println("JWT Validation Error: " + e.getMessage());
            return false;
        }
    }
}
