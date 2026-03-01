package com.a2s.backend.repository;

import com.a2s.backend.model.Design;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface DesignRepository extends JpaRepository<Design, String> {
    List<Design> findByRoomType(String roomType);

    List<Design> findByStyle(String style);
}
