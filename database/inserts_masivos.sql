-- ============================================================
-- INSERTS MASIVOS SoftRelief — 150 usuarios de prueba
-- Contraseña de TODOS: 123456  (hash SHA-256)
-- Nombres naturales: pedro, luis, maria, ... (50 nombres,
--   asignados en ciclos: primera vuelta sin sufijo, luego 001, 002)
-- Correos: nombre@softrelief.test (ej. pedro@softrelief.test)
-- Requiere MySQL 8.0+ (usa CTE recursivo y ROW_NUMBER)
--
-- OJO: ejecutar UNA sola vez. Si se repite, chocará con los
-- correos ya existentes (UNIQUE). Para reiniciar:
--   DELETE FROM usuario WHERE correo LIKE '%@softrelief.test';
--   DELETE FROM preferencia_visual
--   WHERE id_preferencia NOT IN (SELECT id_preferencia FROM usuario);
-- ============================================================

-- 1) Una fila de preferencia_visual por cada usuario nuevo
--    (usuario.id_preferencia es UNIQUE: cada usuario necesita la suya)
INSERT INTO preferencia_visual (id_tema, tamano_fuente, modo_visualizacion)
WITH RECURSIVE nums AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1 FROM nums WHERE n < 150
)
SELECT t.id_tema, 'normal', 'estandar'
FROM nums
CROSS JOIN (SELECT id_tema FROM tema WHERE nombre = 'light') t;

-- 2) Capturar el primer id_preferencia recién insertado
SET @prefs_min := LAST_INSERT_ID();

-- 3) Los 150 usuarios, cada uno con su preferencia visual
INSERT INTO usuario (
    nombre,
    correo,
    contrasena,
    id_rol,
    id_estado,
    id_preferencia
)
WITH RECURSIVE nums AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1 FROM nums WHERE n < 150
),
nombres AS (
    SELECT 'pedro' AS nombre UNION ALL
    SELECT 'luis' UNION ALL
    SELECT 'maria' UNION ALL
    SELECT 'ana' UNION ALL
    SELECT 'carlos' UNION ALL
    SELECT 'lucia' UNION ALL
    SELECT 'miguel' UNION ALL
    SELECT 'sofia' UNION ALL
    SELECT 'jose' UNION ALL
    SELECT 'laura' UNION ALL
    SELECT 'jorge' UNION ALL
    SELECT 'valentina' UNION ALL
    SELECT 'andres' UNION ALL
    SELECT 'camila' UNION ALL
    SELECT 'fernando' UNION ALL
    SELECT 'isabel' UNION ALL
    SELECT 'santiago' UNION ALL
    SELECT 'daniela' UNION ALL
    SELECT 'raul' UNION ALL
    SELECT 'elena' UNION ALL
    SELECT 'hugo' UNION ALL
    SELECT 'paula' UNION ALL
    SELECT 'ivan' UNION ALL
    SELECT 'catalina' UNION ALL
    SELECT 'ricardo' UNION ALL
    SELECT 'julieta' UNION ALL
    SELECT 'marco' UNION ALL
    SELECT 'renata' UNION ALL
    SELECT 'alberto' UNION ALL
    SELECT 'ximena' UNION ALL
    SELECT 'gael' UNION ALL
    SELECT 'fernanda' UNION ALL
    SELECT 'emilio' UNION ALL
    SELECT 'regina' UNION ALL
    SELECT 'leonardo' UNION ALL
    SELECT 'carolina' UNION ALL
    SELECT 'gabriel' UNION ALL
    SELECT 'patricia' UNION ALL
    SELECT 'oscar' UNION ALL
    SELECT 'adriana' UNION ALL
    SELECT 'pablo' UNION ALL
    SELECT 'monica' UNION ALL
    SELECT 'diego' UNION ALL
    SELECT 'alejandra' UNION ALL
    SELECT 'roberto' UNION ALL
    SELECT 'teresa' UNION ALL
    SELECT 'natalia' UNION ALL
    SELECT 'cristian' UNION ALL
    SELECT 'victoria' UNION ALL
    SELECT 'esteban'
),
nombres_ordenados AS (
    SELECT nombre,
           ROW_NUMBER() OVER () AS rn
    FROM nombres
),
prefs AS (
    SELECT id_preferencia,
           ROW_NUMBER() OVER (ORDER BY id_preferencia) AS rn
    FROM preferencia_visual
    WHERE id_preferencia >= @prefs_min
)
SELECT
    CONCAT(
        UPPER(LEFT(no.nombre, 1)),
        SUBSTRING(no.nombre, 2)
    ) AS nombre,
    CONCAT(
        no.nombre,
        CASE
            WHEN (n.n - 1) DIV 50 = 0 THEN ''
            ELSE LPAD((n.n - 1) DIV 50, 3, '0')
        END,
        '@softrelief.test'
    ) AS correo,
    '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92' AS contrasena,
    (SELECT id_rol FROM rol WHERE nombre = 'usuario')              AS id_rol,
    (SELECT id_estado FROM estado_cuenta WHERE nombre = 'activa')  AS id_estado,
    (SELECT p.id_preferencia FROM prefs p WHERE p.rn = n.n)        AS id_preferencia
FROM nums n
JOIN nombres_ordenados no
    ON no.rn = ((n.n - 1) MOD 50) + 1;

-- 4) Verificación: total de usuarios y muestra
SELECT COUNT(*) AS total_usuarios FROM usuario;
SELECT id_usuario, nombre, correo, fecha_registro
FROM usuario
WHERE correo LIKE '%@softrelief.test'
ORDER BY id_usuario
LIMIT 5;
