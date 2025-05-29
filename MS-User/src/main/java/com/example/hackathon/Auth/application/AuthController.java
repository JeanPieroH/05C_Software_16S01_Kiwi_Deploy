package com.example.hackathon.Auth.application;

import com.example.hackathon.Auth.domain.AuthService;
import com.example.hackathon.Auth.dto.RpJwtAuthtentication;
import com.example.hackathon.Auth.dto.RqUserLoginDto;
import com.example.hackathon.Auth.dto.RqUserRegisterDto;
import com.github.dockerjava.zerodep.shaded.org.apache.hc.core5.http.HttpStatus;

import jakarta.servlet.http.HttpServletRequest;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/auth")
public class AuthController {

    @Autowired
    private AuthService authService;

    @PostMapping("/login")
    public ResponseEntity<RpJwtAuthtentication> entrar(@RequestBody RqUserLoginDto rqUserDto) {
        RpJwtAuthtentication token=authService.login(rqUserDto);
        return ResponseEntity.ok(token);
    }

    @PostMapping("/register")
    public ResponseEntity<RpJwtAuthtentication> registrar(@RequestBody RqUserRegisterDto usuario) {
        RpJwtAuthtentication token=authService.register(usuario);
        return ResponseEntity.ok(token);
    }

    @PostMapping("/validate-token")
    public ResponseEntity<Void> validateToken(HttpServletRequest request) {
        if (authService.validate(request)) {
            return ResponseEntity.status(HttpStatus.SC_OK).build();
        }
        else{
            return ResponseEntity.status(HttpStatus.SC_FORBIDDEN).build(); 

        }
    }

    @PostMapping("/validate-token/{role}")
    public ResponseEntity<Void> validateToken(@PathVariable String role, HttpServletRequest request) {
        if (authService.validate(role,request)) {
            return ResponseEntity.status(HttpStatus.SC_OK).build();
        }
        else{
            return ResponseEntity.status(HttpStatus.SC_FORBIDDEN).build(); 
        }
    }

}
