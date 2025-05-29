package com.example.hackathon.Teacher.infrastructure;

import org.springframework.stereotype.Repository;

import com.example.hackathon.Teacher.domain.Teacher;
import com.example.hackathon.Usuario.infrastructure.UsuarioRepository;

@Repository
public interface TeacherRepository extends UsuarioRepository<Teacher>{

}
