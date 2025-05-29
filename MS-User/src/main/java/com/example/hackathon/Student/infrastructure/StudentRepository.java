package com.example.hackathon.Student.infrastructure;

import org.springframework.stereotype.Repository;

import com.example.hackathon.Student.domain.Student;
import com.example.hackathon.Usuario.infrastructure.UsuarioRepository;

@Repository
public interface StudentRepository extends UsuarioRepository<Student> {
    
}
