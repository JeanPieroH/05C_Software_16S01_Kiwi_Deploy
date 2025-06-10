package com.example.hackathon.Teacher.application;

import java.security.Principal;
import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.example.hackathon.Student.domain.Student;
import com.example.hackathon.Student.dto.RpStudentId;
import com.example.hackathon.Teacher.domain.Teacher;
import com.example.hackathon.Teacher.domain.TeacherService;
import com.example.hackathon.Teacher.dto.RpTeacherId;
import com.example.hackathon.Usuario.dto.RqListEmail;

@RestController
@RequestMapping("/teacher")
public class TeacherController {

    @Autowired
    TeacherService teacherService;

    @GetMapping("/me")
    public ResponseEntity<Teacher> getTeacher(Principal principal){
        return ResponseEntity.ok(teacherService.getTeacher(principal));
    }

    @PatchMapping("/me")
    public ResponseEntity<Teacher> patchTeacher(Principal principal,@RequestBody Teacher teacher){
        return ResponseEntity.ok(teacherService.patchTeacher(principal,teacher));
    }

    @PostMapping("/by-ids")
    public ResponseEntity<List<Teacher>> getTeachersByIds(@RequestBody RpTeacherId teacherIds){
        if (teacherIds == null || teacherIds.getTeachers_id().isEmpty()) {
            return ResponseEntity.badRequest().body(List.of());
        }

        List<Teacher> teachers = teacherService.getTeachersByIds(teacherIds.getTeachers_id());
        return ResponseEntity.ok(teachers);
    }

    @PostMapping("/ids-by-email")
    public ResponseEntity<RpTeacherId> getTeachersId(@RequestBody RqListEmail teacherEmails){
        return ResponseEntity.ok(teacherService.getTeachersIdsbyEmail(teacherEmails));
    }
    
}
