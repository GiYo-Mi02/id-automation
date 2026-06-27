-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jun 22, 2026 at 02:56 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `school_id_system`
--

-- --------------------------------------------------------

--
-- Table structure for table `generation_history`
--

CREATE TABLE `generation_history` (
  `id` int(11) NOT NULL,
  `student_id` varchar(50) NOT NULL,
  `full_name` varchar(100) DEFAULT NULL,
  `section` varchar(50) DEFAULT NULL,
  `lrn` varchar(50) DEFAULT NULL,
  `guardian_name` varchar(100) DEFAULT NULL,
  `address` varchar(255) DEFAULT NULL,
  `guardian_contact` varchar(50) DEFAULT NULL,
  `file_path` varchar(255) DEFAULT NULL,
  `status` enum('success','failed','pending') DEFAULT 'success',
  `error_message` text DEFAULT NULL,
  `processing_time_ms` int(11) DEFAULT NULL,
  `timestamp` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `generation_history`
--

INSERT INTO `generation_history` (`id`, `student_id`, `full_name`, `section`, `lrn`, `guardian_name`, `address`, `guardian_contact`, `file_path`, `status`, `error_message`, `processing_time_ms`, `timestamp`) VALUES
(1, '2026-0001', NULL, NULL, NULL, NULL, NULL, NULL, 'data\\output\\front-id\\123456789012.png', 'success', NULL, NULL, '2026-06-22 04:39:37'),
(2, '2026-0001', NULL, NULL, NULL, NULL, NULL, NULL, 'data\\output\\front-id\\123456789012.png', 'success', NULL, NULL, '2026-06-22 04:39:40'),
(3, '2026-0001', NULL, NULL, NULL, NULL, NULL, NULL, 'data\\output\\front-id\\123456789012.png', 'success', NULL, NULL, '2026-06-22 04:42:03'),
(4, 'TCH-2026-001', NULL, NULL, NULL, NULL, NULL, NULL, 'data\\output\\front-id\\TCH-2026-001.png', 'success', NULL, NULL, '2026-06-22 04:42:05'),
(5, '2026-0001', NULL, NULL, NULL, NULL, NULL, NULL, 'data\\output\\front-id\\123456789012.png', 'success', NULL, NULL, '2026-06-22 04:42:06'),
(6, '2026-0002', NULL, NULL, NULL, NULL, NULL, NULL, 'data\\output\\front-id\\123456789013.png', 'success', NULL, NULL, '2026-06-22 04:45:58'),
(7, '2026-0005', NULL, NULL, NULL, NULL, NULL, NULL, 'data\\output\\front-id\\123456789016.png', 'success', NULL, NULL, '2026-06-22 04:47:44'),
(8, '2026-0102', NULL, NULL, NULL, NULL, NULL, NULL, 'data\\output\\front-id\\987654321002.png', 'success', NULL, NULL, '2026-06-22 04:47:52'),
(9, '2026-0103', NULL, NULL, NULL, NULL, NULL, NULL, 'data\\output\\front-id\\987654321003.png', 'success', NULL, NULL, '2026-06-22 04:48:19'),
(10, '2026-0103', NULL, NULL, NULL, NULL, NULL, NULL, 'data\\output\\front-id\\987654321003.png', 'success', NULL, NULL, '2026-06-22 04:48:32'),
(11, '2026-0104', NULL, NULL, NULL, NULL, NULL, NULL, 'data\\output\\front-id\\987654321004.png', 'success', NULL, NULL, '2026-06-22 04:48:57'),
(12, 'TCH-2026-002', NULL, NULL, NULL, NULL, NULL, NULL, 'data\\output\\front-id\\TCH-2026-002.png', 'success', NULL, NULL, '2026-06-22 04:51:50'),
(13, 'TCH-2026-005', NULL, NULL, NULL, NULL, NULL, NULL, 'data\\output\\front-id\\TCH-2026-005.png', 'success', NULL, NULL, '2026-06-22 04:52:41'),
(14, 'TCH-2026-001', NULL, NULL, NULL, NULL, NULL, NULL, 'data\\output\\front-id\\TCH-2026-001.png', 'success', NULL, NULL, '2026-06-22 04:53:15'),
(15, 'TCH-2026-002', NULL, NULL, NULL, NULL, NULL, NULL, 'data\\output\\front-id\\TCH-2026-002.png', 'success', NULL, NULL, '2026-06-22 12:52:55'),
(16, 'TCH-2026-003', NULL, NULL, NULL, NULL, NULL, NULL, 'data\\output\\front-id\\TCH-2026-003.png', 'success', NULL, NULL, '2026-06-22 12:53:22'),
(17, 'TCH-2026-004', NULL, NULL, NULL, NULL, NULL, NULL, 'data\\output\\front-id\\TCH-2026-004.png', 'success', NULL, NULL, '2026-06-22 12:54:47'),
(18, 'TCH-2026-005', NULL, NULL, NULL, NULL, NULL, NULL, 'data\\output\\front-id\\TCH-2026-005.png', 'success', NULL, NULL, '2026-06-22 12:55:47');

-- --------------------------------------------------------

--
-- Table structure for table `id_templates`
--

CREATE TABLE `id_templates` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `template_type` enum('student','teacher','staff','visitor') NOT NULL DEFAULT 'student',
  `school_level` enum('elementary','junior_high','senior_high','college','all') DEFAULT 'all',
  `is_active` tinyint(1) DEFAULT 0,
  `is_active_for_students` tinyint(1) DEFAULT 0,
  `is_active_for_teachers` tinyint(1) DEFAULT 0,
  `is_active_for_staff` tinyint(1) DEFAULT 0,
  `thumbnail` longtext DEFAULT NULL,
  `canvas` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL COMMENT 'Canvas dimensions and background settings' CHECK (json_valid(`canvas`)),
  `front_layers` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL COMMENT 'Array of layer objects for front side' CHECK (json_valid(`front_layers`)),
  `back_layers` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL COMMENT 'Array of layer objects for back side' CHECK (json_valid(`back_layers`)),
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `id_templates`
--

INSERT INTO `id_templates` (`id`, `name`, `template_type`, `school_level`, `is_active`, `is_active_for_students`, `is_active_for_teachers`, `is_active_for_staff`, `thumbnail`, `canvas`, `front_layers`, `back_layers`, `created_at`, `updated_at`) VALUES
(3, 'TAGSCI', 'student', 'junior_high', 0, 0, 0, 0, NULL, '{\"width\": 591, \"height\": 1004, \"backgroundColor\": \"#FFFFFF\"}', '{\"backgroundImage\": null, \"layers\": [{\"id\": \"image-1782046602665\", \"type\": \"image\", \"name\": \"TAGSCI - FRONT NEW\", \"src\": \"http://localhost:8000/uploads/TAGSCI - FRONT NEW_1782046602655.png\", \"field\": null, \"x\": 0, \"y\": 0, \"width\": 590, \"height\": 1000, \"zIndex\": 1, \"visible\": true, \"locked\": false, \"objectFit\": \"cover\", \"borderRadius\": 0}, {\"id\": \"name-1\", \"type\": \"text\", \"name\": \"Full Name\", \"field\": \"full_name\", \"text\": \"STUDENT NAME\", \"x\": 10, \"y\": 310, \"width\": 350, \"height\": 140, \"zIndex\": 2, \"visible\": true, \"locked\": false, \"fontSize\": 54, \"fontFamily\": \"Arial\", \"fontWeight\": \"bold\", \"color\": \"#ffffff\", \"textAlign\": \"left\", \"wordWrap\": true, \"uppercase\": true}, {\"id\": \"image-1781872918202\", \"type\": \"image\", \"name\": \"New Image\", \"field\": \"photo\", \"x\": 220, \"y\": 420, \"width\": 479, \"height\": 601, \"zIndex\": 3, \"visible\": true, \"locked\": false, \"objectFit\": \"cover\", \"borderRadius\": 0}, {\"id\": \"image-1781872958398\", \"type\": \"image\", \"name\": \"Deped\", \"src\": \"http://localhost:8000/uploads/Deped_1781872958381.png\", \"field\": null, \"x\": 30, \"y\": 780, \"width\": 212, \"height\": 106, \"zIndex\": 4, \"visible\": true, \"locked\": false, \"objectFit\": \"cover\", \"borderRadius\": 0}, {\"id\": \"text-1781873015100\", \"type\": \"text\", \"name\": \"New Text\", \"field\": \"section\", \"x\": 340, \"y\": 180, \"width\": 400, \"height\": 70, \"zIndex\": 5, \"visible\": true, \"locked\": false, \"text\": \"New Text\", \"fontSize\": 75, \"fontFamily\": \"Arial\", \"fontWeight\": \"bold\", \"color\": \"#ffffff\", \"textAlign\": \"center\", \"wordWrap\": false, \"rotation\": 270, \"uppercase\": true, \"lowercase\": false}, {\"id\": \"text-1781874929554\", \"type\": \"text\", \"name\": \"New Text\", \"field\": \"static\", \"x\": 40, \"y\": 900, \"width\": 200, \"height\": 30, \"zIndex\": 6, \"visible\": true, \"locked\": false, \"text\": \"S.Y 2026-2027\", \"fontSize\": 28, \"fontFamily\": \"Arial\", \"fontWeight\": \"bold\", \"color\": \"#000000\", \"textAlign\": \"center\", \"wordWrap\": false}]}', '{\"backgroundImage\": null, \"layers\": [{\"id\": \"image-1781872621108\", \"type\": \"image\", \"name\": \"TAGSCI - BACK\", \"src\": \"http://localhost:8000/uploads/TAGSCI - BACK_1781872621105.png\", \"field\": null, \"x\": 0, \"y\": 0, \"width\": 588, \"height\": 1002, \"zIndex\": 1, \"visible\": true, \"locked\": false, \"objectFit\": \"cover\", \"borderRadius\": 0}, {\"id\": \"guardian-1\", \"type\": \"text\", \"name\": \"Guardian\", \"field\": \"guardian_name\", \"text\": \"Guardian: PARENT NAME\", \"x\": 50, \"y\": 380, \"width\": 491, \"height\": 30, \"zIndex\": 3, \"visible\": true, \"locked\": false, \"fontSize\": 34, \"fontFamily\": \"Arial\", \"fontWeight\": \"normal\", \"color\": \"#333333\", \"textAlign\": \"center\", \"wordWrap\": true}, {\"id\": \"address-1\", \"type\": \"text\", \"name\": \"Address\", \"field\": \"address\", \"text\": \"Address Line Here\", \"x\": 220, \"y\": 470, \"width\": 312, \"height\": 50, \"zIndex\": 4, \"visible\": true, \"locked\": false, \"fontSize\": 18, \"fontFamily\": \"Arial\", \"fontWeight\": \"bold\", \"color\": \"#000000\", \"textAlign\": \"left\", \"wordWrap\": true}, {\"id\": \"contact-1\", \"type\": \"text\", \"name\": \"Emergency Contact\", \"field\": \"emergency_contact\", \"text\": \"Emergency: 09171234567\", \"x\": 200, \"y\": 740, \"width\": 283, \"height\": 25, \"zIndex\": 5, \"visible\": true, \"locked\": false, \"fontSize\": 23, \"fontFamily\": \"Arial\", \"fontWeight\": \"bold\", \"color\": \"#333333\", \"textAlign\": \"left\", \"wordWrap\": false}, {\"id\": \"text-1781875193846\", \"type\": \"text\", \"name\": \"Address (Copy)\", \"field\": \"address\", \"text\": \"Address Line Here\", \"x\": 220, \"y\": 660, \"width\": 291, \"height\": 50, \"zIndex\": 6, \"visible\": true, \"locked\": false, \"fontSize\": 18, \"fontFamily\": \"Arial\", \"fontWeight\": \"bold\", \"color\": \"#000000\", \"textAlign\": \"left\", \"wordWrap\": true}]}', '2026-06-19 12:45:47', '2026-06-22 04:51:30'),
(6, 'TAGSCI TEACHER', 'teacher', 'junior_high', 1, 0, 0, 0, NULL, '{\"width\": 591, \"height\": 1004, \"backgroundColor\": \"#FFFFFF\"}', '{\"backgroundImage\": null, \"layers\": [{\"id\": \"image-1781965117208\", \"type\": \"image\", \"name\": \"TAGSCI - New Front\", \"src\": \"http://localhost:8000/uploads/TAGSCI - New Front_1781965117193.png\", \"field\": null, \"x\": 0, \"y\": 0, \"width\": 600, \"height\": 1000, \"zIndex\": 1, \"visible\": true, \"locked\": false, \"objectFit\": \"cover\", \"borderRadius\": 0}, {\"id\": \"legacy-front-photo\", \"type\": \"image\", \"name\": \"Photo\", \"field\": \"photo\", \"x\": 220, \"y\": 420, \"width\": 471, \"height\": 601, \"zIndex\": 2, \"visible\": true, \"locked\": false, \"objectFit\": \"cover\", \"borderRadius\": 0}, {\"id\": \"legacy-front-full_name\", \"type\": \"text\", \"name\": \"Full name\", \"field\": \"full_name\", \"x\": 20, \"y\": 330, \"width\": 410, \"height\": 120, \"zIndex\": 3, \"visible\": true, \"locked\": false, \"fontSize\": 51, \"fontWeight\": \"bold\", \"color\": \"#ffffff\", \"textAlign\": \"left\", \"wordWrap\": true}, {\"id\": \"legacy-front-position\", \"type\": \"text\", \"name\": \"Position\", \"field\": \"position\", \"x\": 290, \"y\": 210, \"width\": 500, \"height\": 70, \"zIndex\": 4, \"visible\": true, \"locked\": false, \"fontSize\": 50, \"fontWeight\": \"bold\", \"color\": \"#ffffff\", \"textAlign\": \"left\", \"wordWrap\": false, \"rotation\": 270, \"uppercase\": true, \"lowercase\": false}, {\"id\": \"legacy-front-static\", \"type\": \"text\", \"name\": \"Static\", \"field\": \"static\", \"x\": 30, \"y\": 900, \"width\": 200, \"height\": 30, \"zIndex\": 6, \"visible\": true, \"locked\": false, \"fontSize\": 27, \"fontWeight\": \"bold\", \"color\": \"#000000\", \"textAlign\": \"center\", \"wordWrap\": false, \"text\": \"SY 2026-2027\"}, {\"id\": \"image-1781965217357\", \"type\": \"image\", \"name\": \"Deped\", \"src\": \"http://localhost:8000/uploads/Deped_1781965217353.png\", \"field\": null, \"x\": 30, \"y\": 780, \"width\": 200, \"height\": 102, \"zIndex\": 7, \"visible\": true, \"locked\": false, \"objectFit\": \"contain\", \"borderRadius\": 0}]}', '{\"backgroundImage\": null, \"layers\": [{\"id\": \"image-1781965478246\", \"type\": \"image\", \"name\": \"TAGSCI - BACK\", \"src\": \"http://localhost:8000/uploads/TAGSCI - BACK_1781965478243.png\", \"field\": null, \"x\": 0, \"y\": 0, \"width\": 590, \"height\": 1010, \"zIndex\": 1, \"visible\": true, \"locked\": false, \"objectFit\": \"cover\", \"borderRadius\": 0}, {\"id\": \"legacy-back-emergency_contact_number\", \"type\": \"text\", \"name\": \"Emergency contact number\", \"field\": \"emergency_contact_number\", \"x\": 200, \"y\": 740, \"width\": 200, \"height\": 40, \"zIndex\": 2, \"visible\": true, \"locked\": false, \"fontSize\": 33, \"fontWeight\": \"bold\", \"color\": \"#000000\", \"textAlign\": \"left\", \"wordWrap\": false}, {\"id\": \"text-1781965509571\", \"type\": \"text\", \"name\": \"New Text\", \"field\": \"emergency_contact_name\", \"x\": 70, \"y\": 380, \"width\": 450, \"height\": 60, \"zIndex\": 3, \"visible\": true, \"locked\": false, \"text\": \"New Text\", \"fontSize\": 32, \"fontFamily\": \"Arial\", \"fontWeight\": \"bold\", \"color\": \"#000000\", \"textAlign\": \"center\", \"wordWrap\": false}, {\"id\": \"text-1781965527218\", \"type\": \"text\", \"name\": \"New Text\", \"field\": \"address\", \"x\": 220, \"y\": 470, \"width\": 320, \"height\": 60, \"zIndex\": 4, \"visible\": true, \"locked\": false, \"text\": \"New Text\", \"fontSize\": 21, \"fontFamily\": \"Arial\", \"fontWeight\": \"bold\", \"color\": \"#000000\", \"textAlign\": \"left\", \"wordWrap\": true}, {\"id\": \"text-1781965539358\", \"type\": \"text\", \"name\": \"New Text\", \"field\": \"address\", \"x\": 200, \"y\": 660, \"width\": 340, \"height\": 70, \"zIndex\": 5, \"visible\": true, \"locked\": false, \"text\": \"New Text\", \"fontSize\": 21, \"fontFamily\": \"Arial\", \"fontWeight\": \"bold\", \"color\": \"#000000\", \"textAlign\": \"left\", \"wordWrap\": true}, {\"id\": \"text-1781965549211\", \"type\": \"text\", \"name\": \"New Text\", \"field\": \"birth_date\", \"x\": 220, \"y\": 610, \"width\": 200, \"height\": 30, \"zIndex\": 6, \"visible\": true, \"locked\": false, \"text\": \"New Text\", \"fontSize\": 25, \"fontFamily\": \"Arial\", \"fontWeight\": \"bold\", \"color\": \"#000000\", \"textAlign\": \"left\", \"wordWrap\": false}]}', '2026-06-20 14:18:16', '2026-06-22 04:52:57'),
(10, 'undefined (Copy)', 'student', 'junior_high', 0, 0, 0, 0, NULL, '{\"width\": 591, \"height\": 1004, \"backgroundColor\": \"#FFFFFF\"}', '{\"backgroundImage\": null, \"layers\": [{\"id\": \"image-1782098336135\", \"type\": \"image\", \"name\": \"1\", \"src\": \"http://localhost:8000/uploads/1_1782098336119.png\", \"field\": null, \"x\": 0, \"y\": 0, \"width\": 590, \"height\": 1000, \"zIndex\": 1, \"visible\": true, \"locked\": false, \"objectFit\": \"cover\", \"borderRadius\": 0}, {\"id\": \"photo-1\", \"type\": \"image\", \"name\": \"Photo\", \"field\": \"photo\", \"x\": 110, \"y\": 240, \"width\": 367, \"height\": 367, \"zIndex\": 2, \"visible\": true, \"locked\": false, \"objectFit\": \"cover\", \"borderRadius\": 8}, {\"id\": \"name-1\", \"type\": \"text\", \"name\": \"Full Name\", \"field\": \"full_name\", \"text\": \"STUDENT NAME\", \"x\": 10, \"y\": 640, \"width\": 570, \"height\": 40, \"zIndex\": 3, \"visible\": true, \"locked\": false, \"fontSize\": 40, \"fontFamily\": \"Arial\", \"fontWeight\": \"bold\", \"color\": \"#d73c3c\", \"textAlign\": \"center\", \"wordWrap\": false, \"uppercase\": true}, {\"id\": \"id-1\", \"type\": \"text\", \"name\": \"ID Number\", \"field\": \"lrn\", \"text\": \"136696210151\", \"x\": 269, \"y\": 701, \"width\": 169, \"height\": 30, \"zIndex\": 4, \"visible\": true, \"locked\": false, \"fontSize\": 26, \"fontFamily\": \"Calibri\", \"fontWeight\": \"bold\", \"color\": \"#333333\", \"textAlign\": \"left\", \"wordWrap\": false}, {\"id\": \"text-1782043367708\", \"type\": \"text\", \"name\": \"New Text\", \"field\": \"static\", \"x\": 380, \"y\": 810, \"width\": 150, \"height\": 30, \"zIndex\": 5, \"visible\": true, \"locked\": false, \"text\": \"MASINOP\", \"fontSize\": 16, \"fontFamily\": \"Arial\", \"fontWeight\": \"bold\", \"color\": \"#000000\", \"textAlign\": \"center\", \"wordWrap\": false, \"uppercase\": true, \"lowercase\": false}, {\"id\": \"text-1782043397674\", \"type\": \"text\", \"name\": \"New Text (Copy)\", \"field\": \"static\", \"x\": 381, \"y\": 853, \"width\": 150, \"height\": 30, \"zIndex\": 6, \"visible\": true, \"locked\": false, \"text\": \"SWAN\", \"fontSize\": 16, \"fontFamily\": \"Arial\", \"fontWeight\": \"bold\", \"color\": \"#000000\", \"textAlign\": \"center\", \"wordWrap\": false, \"uppercase\": true, \"lowercase\": false}]}', '{\"backgroundImage\": null, \"layers\": [{\"id\": \"image-1782099555574\", \"type\": \"image\", \"name\": \"RIZAL_TEMPLATE\", \"src\": \"http://localhost:8000/uploads/RIZAL_TEMPLATE_1782099555571.png\", \"field\": null, \"x\": 10, \"y\": 10, \"width\": 570, \"height\": 980, \"zIndex\": 1, \"visible\": true, \"locked\": false, \"objectFit\": \"cover\", \"borderRadius\": 0}, {\"id\": \"guardian-1\", \"type\": \"text\", \"name\": \"Guardian\", \"field\": \"guardian_name\", \"text\": \"Guardian: PARENT NAME\", \"x\": 200, \"y\": 160, \"width\": 300, \"height\": 80, \"zIndex\": 2, \"visible\": true, \"locked\": false, \"fontSize\": 38, \"fontFamily\": \"Arial\", \"fontWeight\": \"bold\", \"color\": \"#333333\", \"textAlign\": \"left\", \"wordWrap\": true, \"uppercase\": true, \"lowercase\": false}, {\"id\": \"address-1\", \"type\": \"text\", \"name\": \"Address\", \"field\": \"address\", \"text\": \"Address Line Here\", \"x\": 200, \"y\": 290, \"width\": 300, \"height\": 100, \"zIndex\": 3, \"visible\": true, \"locked\": false, \"fontSize\": 26, \"fontFamily\": \"Arial\", \"fontWeight\": \"bold\", \"color\": \"#333333\", \"textAlign\": \"left\", \"wordWrap\": true, \"uppercase\": true, \"lowercase\": false}, {\"id\": \"contact-1\", \"type\": \"text\", \"name\": \"Emergency Contact\", \"field\": \"emergency_contact\", \"text\": \"Emergency: 09171234567\", \"x\": 240, \"y\": 420, \"width\": 210, \"height\": 30, \"zIndex\": 4, \"visible\": true, \"locked\": false, \"fontSize\": 31, \"fontFamily\": \"Arial\", \"fontWeight\": \"bold\", \"color\": \"#333333\", \"textAlign\": \"left\", \"wordWrap\": false, \"uppercase\": true, \"lowercase\": false}]}', '2026-06-22 05:39:44', '2026-06-22 05:39:44');

-- --------------------------------------------------------

--
-- Table structure for table `school_settings`
--

CREATE TABLE `school_settings` (
  `id` int(11) NOT NULL,
  `setting_key` varchar(100) NOT NULL,
  `setting_value` text DEFAULT NULL,
  `setting_type` enum('string','number','boolean','json') DEFAULT 'string',
  `description` text DEFAULT NULL,
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `school_settings`
--

INSERT INTO `school_settings` (`id`, `setting_key`, `setting_value`, `setting_type`, `description`, `updated_at`) VALUES
(1, 'school_name', 'Sample School', 'string', 'Official school name', '2026-06-19 12:45:13'),
(2, 'school_address', '123 School Street, City', 'string', 'School address', '2026-06-19 12:45:13'),
(3, 'school_contact', '(02) 123-4567', 'string', 'School contact number', '2026-06-19 12:45:13'),
(4, 'principal_name', 'Dr. Juan Dela Cruz', 'string', 'Principal name', '2026-06-19 12:45:13'),
(5, 'principal_signature_path', '', 'string', 'Path to principal signature image', '2026-06-19 12:45:13'),
(6, 'school_year', '2025-2026', 'string', 'Current school year', '2026-06-19 12:45:13'),
(7, 'school_logo_path', '', 'string', 'Path to school logo image', '2026-06-19 12:45:13');

-- --------------------------------------------------------

--
-- Table structure for table `staff`
--

CREATE TABLE `staff` (
  `id` int(11) NOT NULL,
  `id_number` varchar(50) NOT NULL,
  `employee_id` varchar(50) NOT NULL,
  `full_name` varchar(200) NOT NULL,
  `department` varchar(100) DEFAULT NULL,
  `position` varchar(100) DEFAULT NULL,
  `contact_number` varchar(50) DEFAULT NULL,
  `emergency_contact_name` varchar(200) DEFAULT NULL,
  `emergency_contact_number` varchar(50) DEFAULT NULL,
  `address` text DEFAULT NULL,
  `birth_date` date DEFAULT NULL,
  `blood_type` varchar(10) DEFAULT NULL,
  `photo_path` varchar(255) DEFAULT NULL,
  `school` varchar(100) DEFAULT '',
  `entry_type` varchar(20) DEFAULT 'import',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `staff`
--

INSERT INTO `staff` (`id`, `id_number`, `employee_id`, `full_name`, `department`, `position`, `contact_number`, `emergency_contact_name`, `emergency_contact_number`, `address`, `birth_date`, `blood_type`, `photo_path`, `school`, `entry_type`, `created_at`, `updated_at`) VALUES
(1, 'STF-2026-001', 'STF-2026-001', 'EMILIO AGUINALDO', 'ADMINISTRATIVE OFFICE', 'ADMINISTRATIVE ASSISTANT I', '09226667777', 'HILARIA AGUINALDO', '09226667778', 'KAWIT CAVITE', '1869-03-22', 'A-', NULL, 'RIZAL HIGH SCHOOL', 'import', '2026-06-22 04:26:49', '2026-06-22 04:26:49'),
(2, 'STF-2026-002', 'STF-2026-002', 'GREGORIO DEL PILAR', 'REGISTRAR OFFICE', 'REGISTRAR CLERK', '09237778888', 'JULIAN DEL PILAR', '09237778889', 'BULACAN BULACAN', '1875-11-14', 'O+', NULL, 'RIZAL HIGH SCHOOL', 'import', '2026-06-22 04:26:49', '2026-06-22 04:26:49'),
(3, 'STF-2026-003', 'STF-2026-003', 'ANTONIO LUNA', 'FINANCE OFFICE', 'CASHIER II', '09248889999', 'LAUREANA NOVICIO', '09248889990', 'BINONDO MANILA', '1866-10-29', 'AB-', NULL, 'RIZAL HIGH SCHOOL', 'import', '2026-06-22 04:26:49', '2026-06-22 04:26:49'),
(4, 'STF-2026-004', 'STF-2026-004', 'JUAN LUNA', 'FACILITIES DEPT', 'BUILDING INSPECTOR', '09259990000', 'PAZ PARDO DE TAVERA', '09259990001', 'BADOC ILOCOS NORTE', '1857-10-24', 'B+', NULL, 'TAGUIG SCIENCE HIGH SCHOOL', 'import', '2026-06-22 04:26:49', '2026-06-22 04:26:49'),
(5, 'STF-2026-005', 'STF-2026-005', 'GABRIELA SILANG', 'LIBRARY SERVICES', 'HEAD LIBRARIAN', '09260001111', 'DIEGO SILANG', '09260001112', 'SANTA ILOCOS SUR', '1731-03-19', 'A+', NULL, 'TAGUIG SCIENCE HIGH SCHOOL', 'import', '2026-06-22 04:26:49', '2026-06-22 04:26:49');

-- --------------------------------------------------------

--
-- Table structure for table `staff_history`
--

CREATE TABLE `staff_history` (
  `id` int(11) NOT NULL,
  `staff_id` varchar(50) DEFAULT NULL,
  `full_name` varchar(200) DEFAULT NULL,
  `department` varchar(100) DEFAULT NULL,
  `position` varchar(100) DEFAULT NULL,
  `file_path` varchar(255) DEFAULT NULL,
  `template_id` int(11) DEFAULT NULL,
  `status` enum('success','failed') DEFAULT 'success',
  `timestamp` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `students`
--

CREATE TABLE `students` (
  `id_number` varchar(50) NOT NULL,
  `full_name` varchar(100) NOT NULL,
  `lrn` varchar(50) DEFAULT NULL,
  `grade_level` varchar(20) DEFAULT NULL,
  `section` varchar(50) DEFAULT NULL,
  `guardian_name` varchar(100) DEFAULT NULL,
  `address` varchar(255) DEFAULT NULL,
  `guardian_contact` varchar(50) DEFAULT NULL,
  `photo_path` varchar(255) DEFAULT NULL,
  `birth_date` date DEFAULT NULL,
  `blood_type` varchar(10) DEFAULT NULL,
  `emergency_contact` varchar(100) DEFAULT NULL,
  `emergency_contact_number` varchar(50) DEFAULT NULL,
  `school_year` varchar(20) DEFAULT '2025-2026',
  `status` enum('active','inactive','graduated','transferred') DEFAULT 'active',
  `school` varchar(100) DEFAULT '',
  `entry_type` varchar(20) DEFAULT 'import',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `students`
--

INSERT INTO `students` (`id_number`, `full_name`, `lrn`, `grade_level`, `section`, `guardian_name`, `address`, `guardian_contact`, `photo_path`, `birth_date`, `blood_type`, `emergency_contact`, `emergency_contact_number`, `school_year`, `status`, `school`, `entry_type`, `created_at`, `updated_at`) VALUES
('2026-0001', 'JUAN DELA CRUZ', '123456789012', 'GRADE 7', 'EINSTEIN', 'MARIA DELA CRUZ', '123 APITONG ST PASIG CITY', '09171234567', NULL, NULL, NULL, NULL, NULL, '2025-2026', 'active', 'RIZAL HIGH SCHOOL', 'import', '2026-06-22 04:26:49', '2026-06-22 04:26:49'),
('2026-0002', 'MARIA CLARA', '123456789013', 'GRADE 7', 'EINSTEIN', 'JOSE IBARRA', '456 DAMPALIT ST PASIG CITY', '09187654321', NULL, NULL, NULL, NULL, NULL, '2025-2026', 'active', 'RIZAL HIGH SCHOOL', 'import', '2026-06-22 04:26:49', '2026-06-22 04:26:49'),
('2026-0003', 'CRISPIN ALONZO', '123456789014', 'GRADE 8', 'NEWTON', 'BASILIO ALONZO', '789 MAYBUNGA PASIG CITY', '09223334444', NULL, NULL, NULL, NULL, NULL, '2025-2026', 'active', 'RIZAL HIGH SCHOOL', 'import', '2026-06-22 04:26:49', '2026-06-22 04:26:49'),
('2026-0004', 'BASILIO ALONZO', '123456789015', 'GRADE 8', 'NEWTON', 'SISA ALONZO', '789 MAYBUNGA PASIG CITY', '09223334444', NULL, NULL, NULL, NULL, NULL, '2025-2026', 'active', 'RIZAL HIGH SCHOOL', 'import', '2026-06-22 04:26:49', '2026-06-22 04:26:49'),
('2026-0005', 'PEDRO PENDUKO', '123456789016', 'GRADE 9', 'GALILEO', 'LINA PENDUKO', '12 RAINBOW ST PASIG CITY', '09334445555', NULL, NULL, NULL, NULL, NULL, '2025-2026', 'active', 'RIZAL HIGH SCHOOL', 'import', '2026-06-22 04:26:49', '2026-06-22 04:26:49'),
('2026-0101', 'ALEXANDER TAN', '987654321001', 'GRADE 10', 'STEPHENSON', 'IRENE TAN', '55 OAK ROAD TAGUIG CITY', '09159998888', NULL, NULL, NULL, NULL, NULL, '2025-2026', 'active', 'TAGUIG SCIENCE HIGH SCHOOL', 'import', '2026-06-22 04:26:49', '2026-06-22 04:26:49'),
('2026-0102', 'BEATRICE GOMEZ', '987654321002', 'GRADE 10', 'STEPHENSON', 'RICARDO GOMEZ', '77 PINE ST TAGUIG CITY', '09168887777', NULL, NULL, NULL, NULL, NULL, '2025-2026', 'active', 'TAGUIG SCIENCE HIGH SCHOOL', 'import', '2026-06-22 04:26:49', '2026-06-22 04:26:49'),
('2026-0103', 'CHELSEA MANALO', '987654321003', 'GRADE 11', 'PROG-A', 'ROBERTO MANALO', '88 CEDAR AVE TAGUIG CITY', '09177776666', NULL, NULL, NULL, NULL, NULL, '2025-2026', 'active', 'TAGUIG SCIENCE HIGH SCHOOL', 'import', '2026-06-22 04:26:49', '2026-06-22 04:26:49'),
('2026-0104', 'DANIEL PADILLA', '987654321004', 'GRADE 11', 'PROG-A', 'CARLA PADILLA', '99 MAPLE RD TAGUIG CITY', '09186665555', NULL, NULL, NULL, NULL, NULL, '2025-2026', 'active', 'TAGUIG SCIENCE HIGH SCHOOL', 'import', '2026-06-22 04:26:49', '2026-06-22 04:26:49'),
('2026-0105', 'ELIZABETH OROPESA', '987654321005', 'GRADE 12', 'STEM-A', 'GLORIA OROPESA', '111 ELM ST TAGUIG CITY', '09195554444', NULL, NULL, NULL, NULL, NULL, '2025-2026', 'active', 'TAGUIG SCIENCE HIGH SCHOOL', 'import', '2026-06-22 04:26:49', '2026-06-22 04:26:49');

-- --------------------------------------------------------

--
-- Table structure for table `teachers`
--

CREATE TABLE `teachers` (
  `employee_id` varchar(50) NOT NULL,
  `full_name` varchar(100) NOT NULL,
  `department` varchar(100) DEFAULT NULL,
  `position` varchar(100) DEFAULT NULL,
  `specialization` varchar(150) DEFAULT NULL,
  `contact_number` varchar(50) DEFAULT NULL,
  `emergency_contact_name` varchar(100) DEFAULT NULL,
  `emergency_contact_number` varchar(50) DEFAULT NULL,
  `address` varchar(255) DEFAULT NULL,
  `birth_date` date DEFAULT NULL,
  `blood_type` varchar(10) DEFAULT NULL,
  `photo_path` varchar(255) DEFAULT NULL,
  `hire_date` date DEFAULT NULL,
  `employment_status` enum('active','inactive','on_leave') DEFAULT 'active',
  `school` varchar(100) DEFAULT '',
  `entry_type` varchar(20) DEFAULT 'import',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `teachers`
--

INSERT INTO `teachers` (`employee_id`, `full_name`, `department`, `position`, `specialization`, `contact_number`, `emergency_contact_name`, `emergency_contact_number`, `address`, `birth_date`, `blood_type`, `photo_path`, `hire_date`, `employment_status`, `school`, `entry_type`, `created_at`, `updated_at`) VALUES
('TCH-2026-001', 'JOSE RIZAL', 'SCIENCE DEPT', 'MASTER TEACHER I', 'BIOLOGY', '09171112222', 'TEODORA ALONZO', '09171112223', 'CALAMBA LAGUNA', '1861-06-19', 'O+', NULL, NULL, 'active', 'RIZAL HIGH SCHOOL', 'import', '2026-06-22 04:26:49', '2026-06-22 04:26:49'),
('TCH-2026-002', 'ANDRES BONIFACIO', 'HISTORY DEPT', 'TEACHER III', 'PHILIPPINE HISTORY', '09182223333', 'GREGORIA DE JESUS', '09182223334', 'TONDO MANILA', '1863-11-30', 'A+', NULL, NULL, 'active', 'RIZAL HIGH SCHOOL', 'import', '2026-06-22 04:26:49', '2026-06-22 04:26:49'),
('TCH-2026-003', 'APOLINARIO MABINI', 'MATHEMATICS DEPT', 'TEACHER II', 'GEOMETRY', '09193334444', 'DIONISIA MABINI', '09193334445', 'TANAUAN BATANGAS', '1864-07-23', 'B-', NULL, NULL, 'active', 'RIZAL HIGH SCHOOL', 'import', '2026-06-22 04:26:49', '2026-06-22 04:26:49'),
('TCH-2026-004', 'MELCHORA AQUINO', 'VALUES DEPT', 'TEACHER III', 'ETHICS', '09204445555', 'JUAN AQUINO', '09204445556', 'NOVALICHES QUEZON CITY', '1812-01-06', 'AB+', NULL, NULL, 'active', 'TAGUIG SCIENCE HIGH SCHOOL', 'import', '2026-06-22 04:26:49', '2026-06-22 04:26:49'),
('TCH-2026-005', 'MARCELO DEL PILAR', 'ENGLISH DEPT', 'MASTER TEACHER II', 'CREATIVE WRITING', '09215556666', 'MARCIANA DEL PILAR', '09215556667', 'BULACAN BULACAN', '1850-08-30', 'O-', NULL, NULL, 'active', 'TAGUIG SCIENCE HIGH SCHOOL', 'import', '2026-06-22 04:26:49', '2026-06-22 04:26:49');

-- --------------------------------------------------------

--
-- Table structure for table `teacher_generation_history`
--

CREATE TABLE `teacher_generation_history` (
  `id` int(11) NOT NULL,
  `employee_id` varchar(50) NOT NULL,
  `full_name` varchar(100) DEFAULT NULL,
  `department` varchar(100) DEFAULT NULL,
  `position` varchar(100) DEFAULT NULL,
  `file_path` varchar(255) DEFAULT NULL,
  `status` enum('success','failed','pending') DEFAULT 'success',
  `error_message` text DEFAULT NULL,
  `processing_time_ms` int(11) DEFAULT NULL,
  `timestamp` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `teacher_history`
--

CREATE TABLE `teacher_history` (
  `id` int(11) NOT NULL,
  `teacher_id` varchar(50) DEFAULT NULL,
  `full_name` varchar(200) DEFAULT NULL,
  `department` varchar(100) DEFAULT NULL,
  `position` varchar(100) DEFAULT NULL,
  `file_path` varchar(255) DEFAULT NULL,
  `template_id` int(11) DEFAULT NULL,
  `status` enum('success','failed') DEFAULT 'success',
  `timestamp` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Stand-in structure for view `v_active_templates`
-- (See below for the actual view)
--
CREATE TABLE `v_active_templates` (
`id` int(11)
,`name` varchar(100)
,`template_type` enum('student','teacher','staff','visitor')
,`school_level` enum('elementary','junior_high','senior_high','college','all')
,`canvas` longtext
,`front_layers` longtext
,`back_layers` longtext
,`created_at` timestamp
,`updated_at` timestamp
);

-- --------------------------------------------------------

--
-- Structure for view `v_active_templates`
--
DROP TABLE IF EXISTS `v_active_templates`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `v_active_templates`  AS SELECT `id_templates`.`id` AS `id`, `id_templates`.`name` AS `name`, `id_templates`.`template_type` AS `template_type`, `id_templates`.`school_level` AS `school_level`, `id_templates`.`canvas` AS `canvas`, `id_templates`.`front_layers` AS `front_layers`, `id_templates`.`back_layers` AS `back_layers`, `id_templates`.`created_at` AS `created_at`, `id_templates`.`updated_at` AS `updated_at` FROM `id_templates` WHERE `id_templates`.`is_active` = 1 ;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `generation_history`
--
ALTER TABLE `generation_history`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_student_id` (`student_id`),
  ADD KEY `idx_timestamp` (`timestamp`);

--
-- Indexes for table `id_templates`
--
ALTER TABLE `id_templates`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_type_level` (`template_type`,`school_level`),
  ADD KEY `idx_active` (`is_active`),
  ADD KEY `idx_templates_active_students` (`is_active_for_students`),
  ADD KEY `idx_templates_active_teachers` (`is_active_for_teachers`),
  ADD KEY `idx_templates_active_staff` (`is_active_for_staff`);

--
-- Indexes for table `school_settings`
--
ALTER TABLE `school_settings`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `setting_key` (`setting_key`);

--
-- Indexes for table `staff`
--
ALTER TABLE `staff`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uk_staff_id_number` (`id_number`),
  ADD UNIQUE KEY `uk_staff_employee_id` (`employee_id`),
  ADD KEY `idx_staff_school` (`school`);

--
-- Indexes for table `staff_history`
--
ALTER TABLE `staff_history`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_staff_history_staff_id` (`staff_id`),
  ADD KEY `idx_staff_history_timestamp` (`timestamp`);

--
-- Indexes for table `students`
--
ALTER TABLE `students`
  ADD PRIMARY KEY (`id_number`),
  ADD KEY `idx_full_name` (`full_name`),
  ADD KEY `idx_section` (`section`),
  ADD KEY `idx_grade_level` (`grade_level`),
  ADD KEY `idx_students_created_at` (`created_at`),
  ADD KEY `idx_students_school` (`school`);

--
-- Indexes for table `teachers`
--
ALTER TABLE `teachers`
  ADD PRIMARY KEY (`employee_id`),
  ADD KEY `idx_full_name` (`full_name`),
  ADD KEY `idx_department` (`department`),
  ADD KEY `idx_position` (`position`),
  ADD KEY `idx_status` (`employment_status`),
  ADD KEY `idx_teachers_school` (`school`);

--
-- Indexes for table `teacher_generation_history`
--
ALTER TABLE `teacher_generation_history`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_employee_id` (`employee_id`),
  ADD KEY `idx_timestamp` (`timestamp`);

--
-- Indexes for table `teacher_history`
--
ALTER TABLE `teacher_history`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_teacher_history_teacher_id` (`teacher_id`),
  ADD KEY `idx_teacher_history_timestamp` (`timestamp`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `generation_history`
--
ALTER TABLE `generation_history`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=19;

--
-- AUTO_INCREMENT for table `id_templates`
--
ALTER TABLE `id_templates`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `school_settings`
--
ALTER TABLE `school_settings`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=363;

--
-- AUTO_INCREMENT for table `staff`
--
ALTER TABLE `staff`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `staff_history`
--
ALTER TABLE `staff_history`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `teacher_generation_history`
--
ALTER TABLE `teacher_generation_history`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `teacher_history`
--
ALTER TABLE `teacher_history`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
