package com.a2s.backend.config;

import com.a2s.backend.model.Design;
import com.a2s.backend.model.Product;
import com.a2s.backend.repository.DesignRepository;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.Arrays;
import java.util.List;
import java.util.ArrayList;

@Configuration
public class DataInitializer {

        @Bean
        CommandLineRunner initDatabase(DesignRepository repository) {
                return args -> {
                        if (repository.count() == 0) {
                                System.out.println("Seeding designs into database...");

                                // ── Design 1: Urban Zen Sanctuary ──────────────────────────────
                                Design d1 = new Design();
                                d1.setTitle("Urban Zen Sanctuary");
                                d1.setDescription(
                                                "A modern minimalist living room optimized for small Indian apartments.");
                                d1.setImage("https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?q=80&w=2000&auto=format&fit=crop");
                                d1.setGallery(Arrays.asList(
                                                "https://images.unsplash.com/photo-1618221415201-1e8c075677d2?w=800&auto=format&fit=crop",
                                                "https://images.unsplash.com/photo-1618219908412-a29a1bb7b86e?w=800&auto=format&fit=crop"));
                                d1.setRoomType("Living Room");
                                d1.setStyle("Modern");
                                d1.setTotalCost(34698.0);
                                d1.setTags(Arrays.asList("Compact", "Budget Friendly", "Green Accents"));
                                d1.setProducts(Arrays.asList(
                                                createProduct("Berkeley 3-Seater Sofa", "Pepperfry", "Furniture",
                                                                28999.0,
                                                                "84\"W x 38\"D x 34\"H", "Forest Green", "#2D4F1E",
                                                                "Performance Velvet", "Pepperfry",
                                                                "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=400&auto=format&fit=crop",
                                                                "A masterpiece of modern comfort, featuring a kiln-dried solid wood frame upholstered in premium 400 GSM performance velvet.",
                                                                Arrays.asList(
                                                                                "https://images.unsplash.com/photo-1493663284031-b7e3aefcae8e?w=400&auto=format&fit=crop",
                                                                                "https://images.unsplash.com/photo-1550581190-9c1c48d21d6c?w=400&auto=format&fit=crop")),
                                                createProduct("Olive Grove Emulsion", "Asian Paints", "Paint", 3200.0,
                                                                null, "Olive Grove", "#556B2F", "Acrylic Emulsion",
                                                                "Asian Paints",
                                                                "https://images.unsplash.com/photo-1589939705384-5185137a7f0f?w=400&auto=format&fit=crop",
                                                                "A rich, matte-finish acrylic emulsion that brings the tranquility of nature into your living realm.",
                                                                null),
                                                createProduct("LACK Coffee Table", "IKEA", "Furniture", 2499.0,
                                                                "90x55 cm",
                                                                "White", "#FFFFFF", "Particleboard", "IKEA",
                                                                "https://images.unsplash.com/photo-1611269154421-4e27233ac5c7?w=400&auto=format&fit=crop",
                                                                "The LACK coffee table embodies functional minimalism.",
                                                                Arrays.asList("https://images.unsplash.com/photo-1533090161767-e6ffed986c88?w=400&auto=format&fit=crop"))));

                                // ── Design 2: Bohemian Rhapsody ────────────────────────────────
                                Design d2 = new Design();
                                d2.setTitle("Bohemian Rhapsody");
                                d2.setDescription("Vibrant colors and textures for a lively family space.");
                                d2.setImage("https://images.unsplash.com/photo-1586023492125-27b2c045efd7?q=80&w=2000&auto=format&fit=crop");
                                d2.setRoomType("Living Room");
                                d2.setStyle("Boho");
                                d2.setTotalCost(44700.0);
                                d2.setTags(Arrays.asList("Colorful", "Textured", "Artistic"));
                                d2.setProducts(Arrays.asList(
                                                createProduct("Macrame Wall Hanging", "CraftVilla", "Decor", 3500.0,
                                                                "60x90 cm", "Ivory", "#FFFFF0", "Cotton Rope",
                                                                "CraftVilla",
                                                                "https://images.unsplash.com/photo-1594040226829-7f251ab46d80?w=400&auto=format&fit=crop",
                                                                "Hand-woven by local artisans, this macrame piece features intricate nautical knots.",
                                                                null),
                                                createProduct("Arteriors Floor Lamp", "Kapoor Lights", "Lighting",
                                                                5500.0,
                                                                null, "Brass", "#B5A642", "Brass", "Amazon India",
                                                                "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=400&auto=format&fit=crop",
                                                                "An architectural statement in brass and light.",
                                                                null),
                                                createProduct("Jaipuri Hand-Knotted Rug", "Jaipur Rugs", "Decor",
                                                                12000.0,
                                                                "5x8 ft", "Multicolor", "#E8834A", "Wool",
                                                                "Jaipur Rugs",
                                                                "https://images.unsplash.com/photo-1575414003591-4a6ab5f7ce69?w=400&auto=format&fit=crop",
                                                                "A labor of love that takes months to weave.",
                                                                null),
                                                createProduct("Boho Accent Chair", "Urban Ladder", "Furniture", 15500.0,
                                                                "28\"W x 30\"D x 35\"H", "Terracotta", "#C04000",
                                                                "Linen Fabric", "Urban Ladder",
                                                                "https://images.unsplash.com/photo-1567538096630-e0c55bd6374c?w=400&auto=format&fit=crop",
                                                                "Ergonomically designed for long reflections.",
                                                                null),
                                                createProduct("Rattan Side Table", "Pepperfry", "Furniture", 8200.0,
                                                                "45x45x55 cm", "Natural Brown", "#8B6914", "Rattan",
                                                                "Pepperfry",
                                                                "https://images.unsplash.com/photo-1631679706909-1844bbd07221?w=400&auto=format&fit=crop",
                                                                "Lightweight yet structurally sound side table.",
                                                                null)));

                                // ── Design 3: Minimalist Nordic Bedroom ───────────────────────
                                Design d3 = new Design();
                                d3.setTitle("Minimalist Nordic Bedroom");
                                d3.setDescription("Calm tones and functional furniture for deep rest.");
                                d3.setImage("https://images.unsplash.com/photo-1595526114035-0d45ed16cfbf?q=80&w=2000&auto=format&fit=crop");
                                d3.setRoomType("Bedroom");
                                d3.setStyle("Minimal");
                                d3.setTotalCost(42000.0);
                                d3.setTags(Arrays.asList("Peaceful", "White", "Wood"));
                                d3.setProducts(Arrays.asList(
                                                createProduct("Platform Bed Frame", "IKEA", "Furniture", 18000.0,
                                                                "Queen 160x200 cm", "White Oak", "#F5F0E8",
                                                                "Solid Pine", "IKEA",
                                                                "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?w=400&auto=format&fit=crop",
                                                                "A cornerstone of Scandinavian utility.",
                                                                null),
                                                createProduct("Nordic Bedside Lamp", "Ikea", "Lighting", 5500.0,
                                                                null, "White", "#FFFFFF", "Metal", "IKEA",
                                                                "https://images.unsplash.com/photo-1540932239986-30128078f3c5?w=400&auto=format&fit=crop",
                                                                "Diffusion and detail. Minimalist task lamp.",
                                                                null),
                                                createProduct("Cotton Waffle Duvet Cover", "H&M Home", "Decor", 6800.0,
                                                                "Queen 220x240 cm", "Off White", "#FAF9F6",
                                                                "100% Cotton", "H&M Home",
                                                                "https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=400&auto=format&fit=crop",
                                                                "Tactile comfort in every thread.",
                                                                null),
                                                createProduct("Floating Wooden Shelf", "Wooden Street", "Furniture",
                                                                4200.0,
                                                                "90x20 cm", "Walnut Brown", "#773F1A", "Sheesham Wood",
                                                                "Wooden Street",
                                                                "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=400&auto=format&fit=crop",
                                                                "A gravity-defying display of heritage.",
                                                                null),
                                                createProduct("Jute Bedside Rug", "Fab India", "Decor", 7500.0,
                                                                "2x3 ft each (pair)", "Beige", "#F5F5DC", "Jute",
                                                                "Fab India",
                                                                "https://images.unsplash.com/photo-1600166898405-da9535204843?w=400&auto=format&fit=crop",
                                                                "Earthy and resilient rug.",
                                                                null)));

                                // ── Design 4: Heritage Luxury Dining ──────────────────────────
                                Design d4 = new Design();
                                d4.setTitle("Heritage Luxury Dining");
                                d4.setDescription("Traditional Indian aesthetics meeting modern comfort.");
                                d4.setImage("https://images.unsplash.com/photo-1617806118233-18e1de247200?q=80&w=2000&auto=format&fit=crop");
                                d4.setRoomType("Dining");
                                d4.setStyle("Traditional");
                                d4.setTotalCost(85000.0);
                                d4.setTags(Arrays.asList("Royal", "Wood", "Ornate"));
                                d4.setProducts(Arrays.asList(
                                                createProduct("Sheesham Wood Dining Table 6-Seater", "Wooden Street",
                                                                "Furniture", 45000.0,
                                                                "180x90x76 cm", "Dark Walnut", "#4A2C0A",
                                                                "Solid Sheesham", "Wooden Street",
                                                                "https://images.unsplash.com/photo-1549497538-303791108f95?w=400&auto=format&fit=crop",
                                                                "The centerpiece of heritage dining.",
                                                                null),
                                                createProduct("Jaipuri Hand-Knotted Rug", "Jaipur Rugs", "Decor",
                                                                12000.0,
                                                                "6x9 ft", "Red and Gold", "#8B0000", "Wool",
                                                                "Jaipur Rugs",
                                                                "https://images.unsplash.com/photo-1575414003591-4a6ab5f7ce69?w=400&auto=format&fit=crop",
                                                                "A royal foundation.",
                                                                null),
                                                createProduct("Brass Chandelier", "Envisage India", "Lighting", 8500.0,
                                                                "60cm diameter", "Antique Brass", "#B5A642", "Brass",
                                                                "Amazon India",
                                                                "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&auto=format&fit=crop",
                                                                "A crown of light.",
                                                                null),
                                                createProduct("Teak Wood Sideboard", "Pepperfry", "Furniture", 9500.0,
                                                                "120x40x80 cm", "Teak Brown", "#8B5E3C", "Teak Wood",
                                                                "Pepperfry",
                                                                "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=400&auto=format&fit=crop",
                                                                "Functional heritage sideboard.",
                                                                null),
                                                createProduct("Madhubani Art Frame Set", "Fab India", "Decor", 10000.0,
                                                                "Set of 3, 12x16 inch each", "Multicolor", "#C41E3A",
                                                                "Canvas", "Fab India",
                                                                "https://images.unsplash.com/photo-1602928298849-325cec8771a5?w=400&auto=format&fit=crop",
                                                                "Living history. Hand-painted art.",
                                                                null)));

                                // ── Design 5: Modern Loft Kitchen ─────────────────────────────
                                Design d5 = new Design();
                                d5.setTitle("Modern Loft Kitchen");
                                d5.setDescription("Open concept kitchen with industrial touches.");
                                d5.setImage("https://images.unsplash.com/photo-1556911220-e15b29be8c8f?q=80&w=2000&auto=format&fit=crop");
                                d5.setRoomType("Kitchen");
                                d5.setStyle("Industrial");
                                d5.setTotalCost(120000.0);
                                d5.setTags(Arrays.asList("Industrial", "Open", "Grey"));
                                d5.setProducts(Arrays.asList(
                                                createProduct("Modular Kitchen Set", "Sleek", "Furniture", 5500.0,
                                                                "L-shape 8x6 ft", "Matte Grey", "#808080",
                                                                "MDF + Plywood", "Sleek Kitchens",
                                                                "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400&auto=format&fit=crop",
                                                                "Precision-engineered utility.",
                                                                null),
                                                createProduct("Pendant Track Lights", "Philips", "Lighting", 18000.0,
                                                                "3-light track, 120cm", "Matte Black", "#1C1C1C",
                                                                "Aluminium", "Philips India",
                                                                "https://images.unsplash.com/photo-1565814329452-e1efa11c5b89?w=400&auto=format&fit=crop",
                                                                "Industrial clarity lights.",
                                                                null),
                                                createProduct("Industrial Bar Stools (2pc)", "Urban Ladder",
                                                                "Furniture", 22000.0,
                                                                "H: 75 cm", "Black Metal", "#2B2B2B", "Steel + Leather",
                                                                "Urban Ladder",
                                                                "https://images.unsplash.com/photo-1567538096630-e0c55bd6374c?w=400&auto=format&fit=crop",
                                                                "Rugged sophistication stools.",
                                                                null),
                                                createProduct("Cement Grey Wall Paint", "Asian Paints", "Paint",
                                                                12000.0,
                                                                null, "Cement Grey", "#9E9E9E", "Acrylic Emulsion",
                                                                "Asian Paints",
                                                                "https://images.unsplash.com/photo-1589939705384-5185137a7f0f?w=400&auto=format&fit=crop",
                                                                "The base of industrial realms.",
                                                                null),
                                                createProduct("Stainless Steel Sink with Faucet", "Franke", "Decor",
                                                                13000.0,
                                                                "90x50 cm Double Bowl", "Steel", "#C0C0C0",
                                                                "Stainless Steel", "Franke India",
                                                                "https://images.unsplash.com/photo-1556909172-54557c7e4fb7?w=400&auto=format&fit=crop",
                                                                "Surgical precision double-bowl sink.",
                                                                null)));

                                // ── Design 6: Luxury Royal Suite ──────────────────────────────
                                Design d6 = new Design();
                                d6.setTitle("Luxury Royal Suite");
                                d6.setDescription("Opulent details and rich textures for a majestic feel.");
                                d6.setImage("https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?auto=format&fit=crop&q=80&w=800");
                                d6.setRoomType("Living Room");
                                d6.setStyle("Luxury");
                                d6.setTotalCost(175000.0);
                                d6.setTags(Arrays.asList("Royal", "Gold", "Velvet"));
                                d6.setProducts(Arrays.asList(
                                                createProduct("Royal Chesterfield Sofa", "Pepperfry", "Furniture",
                                                                85000.0,
                                                                "96\"W x 42\"D x 36\"H", "Royal Blue", "#002366",
                                                                "Premium Velvet", "Pepperfry",
                                                                "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=400&auto=format&fit=crop",
                                                                "Exuding timeless majesty sofa.",
                                                                null),
                                                createProduct("Gold Leaf Coffee Table", "Urban Ladder", "Furniture",
                                                                28999.0,
                                                                "120x60x45 cm", "Gold & Glass", "#FFD700",
                                                                "Metal + Tempered Glass", "Urban Ladder",
                                                                "https://images.unsplash.com/photo-1611269154421-4e27233ac5c7?w=400&auto=format&fit=crop",
                                                                "A focal point of artisanal luxury.",
                                                                null),
                                                createProduct("Crystal Chandelier", "Envisage India", "Lighting",
                                                                22000.0,
                                                                "80cm diameter", "Gold", "#CFB53B", "Crystal + Brass",
                                                                "Amazon India",
                                                                "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&auto=format&fit=crop",
                                                                "Pure luminescence chandelier.",
                                                                null),
                                                createProduct("Silk Persian Rug", "Jaipur Rugs", "Decor", 18000.0,
                                                                "8x10 ft", "Deep Burgundy", "#800020", "Silk",
                                                                "Jaipur Rugs",
                                                                "https://images.unsplash.com/photo-1575414003591-4a6ab5f7ce69?w=400&auto=format&fit=crop",
                                                                "An heirloom for the ages rug.",
                                                                null),
                                                createProduct("Ornate Wall Mirror", "Fab India", "Decor", 21001.0,
                                                                "90x120 cm", "Antique Gold", "#B8860B",
                                                                "Carved Teak Frame", "Fab India",
                                                                "https://images.unsplash.com/photo-1590502160462-58b41354f588?w=400&auto=format&fit=crop",
                                                                "Reflecting heritage ornate mirror.",
                                                                null)));

                                repository.saveAll(Arrays.asList(d1, d2, d3, d4, d5, d6));
                                System.out.println("Designs successfully seeded!");
                        }
                };
        }

        private Product createProduct(String name, String brand, String category, Double price,
                        String dimensions, String color, String colorHex,
                        String material, String vendor, String image, String description, List<String> gallery) {
                Product p = new Product();
                p.setName(name);
                p.setBrand(brand);
                p.setCategory(category);
                p.setPrice(price);
                p.setDimensions(dimensions);
                p.setColor(color);
                p.setColorHex(colorHex);
                p.setMaterial(material);
                p.setVendor(vendor);
                p.setAffiliateLink("#");
                p.setImage(image);
                p.setDescription(description);
                p.setGallery(gallery != null ? gallery : new ArrayList<>());
                return p;
        }
}
