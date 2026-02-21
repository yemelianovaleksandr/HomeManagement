INSERT INTO apartments (number, floor, type, square_meters) VALUES
('101', 1, 'Студія', 32.5),
('102', 1, 'Однокімнатна', 45.0),
('201', 2, 'Двокімнатна', 65.2),
('202', 2, 'Трикімнатна', 88.0),
('301', 3, 'Чотирикімнатна', 110.5),
('302', 3, 'Студія', 35.0);

INSERT INTO residents (full_name, email, phone, birth_date) VALUES
('Іван Петренко', 'ivan.p@email.com', '+380501112233', '1990-05-15'),
('Марія Коваленко', 'mariya.k@email.com', '+380674445566', '1992-10-20'),
('Олексій Швець', 'olexiy.sh@email.com', '+380937778899', '1985-03-12'),
('Олена Сидорчук', 'olena.s@email.com', '+380509990011', '1995-12-01');

INSERT INTO residency (resident_id, apartment_id, move_in_date) VALUES
(1, 3, '2023-01-10'),
(2, 3, '2023-01-12');


INSERT INTO residency (resident_id, apartment_id, move_in_date) VALUES
(3, 5, '2023-06-20');

INSERT INTO residency (resident_id, apartment_id, move_in_date) VALUES
(4, 1, '2024-02-15');
