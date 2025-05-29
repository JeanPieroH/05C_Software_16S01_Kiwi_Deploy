package com.example.hackathon.Auth.domain;

import com.example.hackathon.Auth.dto.RpJwtAuthtentication;
import com.example.hackathon.Auth.dto.RqUserLoginDto;
import com.example.hackathon.Auth.dto.RqUserRegisterDto;
import com.example.hackathon.Exceptions.NotFoundException;
import com.example.hackathon.Exceptions.UniqueConstraintException;
import com.example.hackathon.Student.domain.Student;
import com.example.hackathon.Student.infrastructure.StudentRepository;
import com.example.hackathon.Teacher.domain.Teacher;
import com.example.hackathon.Teacher.infrastructure.TeacherRepository;
import com.example.hackathon.Usuario.domain.Role;
import com.example.hackathon.Usuario.domain.Usuario;
import com.example.hackathon.Usuario.infrastructure.UsuarioRepository;

import jakarta.servlet.http.HttpServletRequest;

import org.modelmapper.ModelMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.util.Date;
import java.util.Optional;

@Service
public class AuthService {
    @Autowired
    UsuarioRepository usuarioRepository;
    
    @Autowired
    TeacherRepository teacherRepository;
    @Autowired
    StudentRepository studentRepository;


    @Autowired
    PasswordEncoder passwordEncoder;
    @Autowired
    JwtService jwtService;
    @Autowired
    private ModelMapper modelMapper;

    public RpJwtAuthtentication login(RqUserLoginDto rqUserDto) {
        Optional<Usuario> user= usuarioRepository.findByEmail(rqUserDto.getEmail());

        if (user.isEmpty()) throw new NotFoundException("Email is not registered");
        if (!passwordEncoder.matches(rqUserDto.getPassword(), user.get().getPassword()))
            throw new IllegalArgumentException("Password is incorrect");

        RpJwtAuthtentication token = new RpJwtAuthtentication();
        token.setToken(jwtService.generateToken(user.get()));
        return token;
    }

    public RpJwtAuthtentication register(RqUserRegisterDto usuario){
        Optional<Usuario> user = usuarioRepository.findByEmail(usuario.getEmail());
        usuario.setPassword(passwordEncoder.encode(usuario.getPassword()));
        if (user.isPresent()) throw new UniqueConstraintException("Email is already registered");

        RpJwtAuthtentication token = new RpJwtAuthtentication();
        usuario.setRegistration_date(new Date());
        if(usuario.getRole()==Role.STUDENT){
            Student usuarioNuevo = modelMapper.map(usuario, Student.class);
            studentRepository.save(usuarioNuevo);
            token.setToken(jwtService.generateToken(usuarioNuevo));

        }
        else if (usuario.getRole()==Role.TEACHER){
            Teacher usuarioNuevo = modelMapper.map(usuario, Teacher.class);
            teacherRepository.save(usuarioNuevo);
            token.setToken(jwtService.generateToken(usuarioNuevo));
        }

        return token;
    }
    
    public boolean validate(HttpServletRequest request){
        String authHeader = request.getHeader("Authorization");
        String jwt= authHeader.substring(7);
        String userEmail = jwtService.extractUsername(jwt);
        
        return jwtService.isTokenValid(jwt, userEmail);        
    }

    public boolean validate(String role, HttpServletRequest request){
        if(!validate(request))
            return false;

        String authHeader = request.getHeader("Authorization");
        String jwt= authHeader.substring(7);

        System.out.println(jwtService.extractRole(jwt));

        if (!jwtService.extractRole(jwt).toLowerCase().equals(role.toLowerCase())){
            return false;
        }

        return true;        
    }
}
