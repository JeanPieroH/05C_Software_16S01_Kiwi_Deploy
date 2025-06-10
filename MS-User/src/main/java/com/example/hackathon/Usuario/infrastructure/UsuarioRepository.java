package com.example.hackathon.Usuario.infrastructure;
import java.util.List;
import com.example.hackathon.Usuario.domain.Usuario;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface UsuarioRepository<T extends Usuario> extends JpaRepository<T, Long> {
    Optional<T> findByEmail(String correo);
    List<T> findAllById(Iterable<Long> ids);
    List<T> findByEmailIn(List<String> emails);
}
