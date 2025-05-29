package com.example.hackathon.Student.application;

import java.security.Principal;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.example.hackathon.Student.domain.Student;
import com.example.hackathon.Student.domain.StudentService;


@RestController
@RequestMapping("/student")
public class StudentController {
    @Autowired
    StudentService studentService;

    @GetMapping("/me")
    public ResponseEntity<Student> getStudent(Principal principal){
        return ResponseEntity.ok(studentService.getStudent(principal));
    }

    @PatchMapping("/me")
    public ResponseEntity<Student> patchStudent(Principal principal,@RequestBody Student student){
        return ResponseEntity.ok(studentService.patchStudent(principal,student));
    }

}
