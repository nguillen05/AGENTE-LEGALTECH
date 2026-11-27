"""
Script para generar contratos de muestra realistas para pruebas del Agente CLM.
Genera archivos en formato .docx y .txt.
"""

import os
import docx

EJEMPLOS_DIR = os.path.join(os.path.dirname(__file__), "ejemplos_contratos")
os.makedirs(EJEMPLOS_DIR, exist_ok=True)

# 1. CONTRATO DE PRESTACIÓN DE SERVICIOS TECNOLÓGICOS (SAAS)
saas_text = """CONTRATO DE PRESTACIÓN DE SERVICIOS DE SOFTWARE Y DESARROLLO TECNOLÓGICO

COMPARECIENTES:
De una parte, CLOUDTECH SOLUTIONS S.A.S., con RUC 1793849182001, debidamente representada por su Gerente General, Ing. Roberto Andrade (en adelante, el "PROVEEDOR").
Y de otra parte, INVERSIONES & RETAIL DEL PACÍFICO CÍA. LTDA., con RUC 0992384756001, representada legalmente por la Dra. Mariana Gómez (en adelante, el "CLIENTE").

Las partes acuerdan suscribir el presente Contrato de Servicios sujeto a las siguientes cláusulas:

PRIMERA: OBJETO DEL CONTRATO
El PROVEEDOR se obliga a brindar al CLIENTE el acceso a su plataforma en la nube (SaaS) de gestión logística, así como los servicios profesionales de integración con el ERP empresarial y mantenimiento correctivo/evolutivo durante el término del acuerdo.

SEGUNDA: PLAZO DE VIGENCIA Y PRÓRROGA AUTOMÁTICA
El presente contrato tendrá una vigencia inicial de doce (12) meses a partir de la fecha de suscripción. El contrato se prorrogará automáticamente por períodos sucesivos de un (1) año adicional cada uno, a menos que cualquiera de las partes comunique a la otra su decisión en contrario con al menos noventa (90) días de anticipación a la fecha de vencimiento respectivo.

TERCERA: PRECIO, CONDICIONES DE PAGO Y FACTURACIÓN
El CLIENTE pagará al PROVEEDOR una tarifa mensual fija recurrente de USD 4,500.00 (cuatro mil quinientos dólares de los Estados Unidos de América) más el Impuesto al Valor Agregado (IVA). Los pagos se realizarán dentro de los primeros cinco (5) días calendario de cada mes mediante transferencia bancaria.
En caso de retraso en el pago, se devengará una penalidad por mora equivalente al interés máximo legal permitido por el Banco Central del Ecuador, más un recargo administrativo del 3% mensual sobre el saldo adeudado.

CUARTA: OBLIGACIONES DEL PROVEEDOR
a) Garantizar una disponibilidad del servicio del 99.5% (SLA).
b) Brindar soporte técnico en horario laboral y resolución de incidencias críticas en un lapso no mayor a 4 horas.
c) Mantener copias de seguridad diarias y encriptadas de toda la información corporativa del CLIENTE.

QUINTA: OBLIGACIONES DEL CLIENTE
a) Realizar el pago íntegro y puntual de los honorarios pactados.
b) Designar un interlocutor técnico calificado para coordinar los accesos y pruebas de integración.
c) No realizar ingeniería inversa, descompilar ni ceder las credenciales de acceso a terceros ajenos a la organización.

SEXTA: PROPIEDAD INTELECTUAL
El PROVEEDOR conserva todos los derechos de autor, patentes, marcas y propiedad intelectual sobre el software base, librerías, algoritmos y código fuente. El CLIENTE conserva la titularidad exclusiva sobre sus bases de datos y la información de sus operaciones comerciales.

SÉPTIMA: CONFIDENCIALIDAD
Ambas partes se comprometen a guardar estricta reserva y secreto profesional respecto a toda información técnica, financiera y comercial intercambiada. Esta obligación subsistirá durante tres (3) años posteriores a la terminación del presente contrato.

OCTAVA: RESPONSABILIDAD E INDEMNIDAD
La responsabilidad patrimonial total acumulada del PROVEEDOR derivada de cualquier reclamación relacionada con este contrato estará limitada a la suma efectivamente pagada por el CLIENTE en los últimos tres (3) meses de servicio. En ningún caso las partes responderán por lucro cesante, daños punitivos o pérdidas indirectas.

NOVENA: TERMINACIÓN ANTICIPADA
El presente contrato podrá darse por terminado por:
1. Incumplimiento grave de las obligaciones contractuales que no fuere subsanado dentro de un término de quince (15) días posteriores a la notificación escrita.
2. Quiebra, concurso de acreedores o liquidación de cualquiera de las partes.
3. Mutuo acuerdo suscrito por escrito.

DÉCIMA: LEY APLICABLE Y RESOLUCIÓN DE CONTROVERSIAS
El presente acuerdo se rige por las leyes de la República del Ecuador. Cualquier controversia será sometida a mediación en el Centro de Arbitraje y Mediación de la Cámara de Comercio de Quito. En caso de no alcanzarse acuerdo, se resolverá mediante arbitraje en derecho conforme al reglamento de dicho Centro.

Dado y firmado en la ciudad de Quito D.M., a los 15 días del mes de enero de 2026.
"""

# 2. ACUERDO DE CONFIDENCIALIDAD Y NO DIVULGACIÓN (NDA)
nda_text = """ACUERDO DE CONFIDENCIALIDAD Y NO DIVULGACIÓN BILATERAL (NDA)

ENTRE LOS SUSCRITOS:
1. FINTECH INNOVATION CORP., sociedad constituida con domicilio principal en Quito, Ecuador, representada por su Director Ejecutivo, Dr. Alejandro Serrano.
2. VANGUARD CAPITAL ADVISORS S.A., con domicilio principal en Guayaquil, Ecuador, representada por su Gerente de Inversiones, Econ. Valeria Moncayo.

CONSIDERANDO:
Que las Partes tienen la intención de evaluar una potencial transacción comercial de inversión y financiamiento estratégico (en adelante, el "Proyecto"), y en el marco de tales conversaciones requerirán compartir información de carácter estrictamente confidencial.

CLÁUSULA PRIMERA: INFORMACIÓN CONFIDENCIAL
Se entenderá por "Información Confidencial" cualquier dato técnico, financiero, contable, proyecciones de negocio, listas de clientes, código de software, modelos matemáticos, análisis de mercado o secretos empresariales compartidos por escrito, verbalmente o por medios electrónicos.

CLÁUSULA SEGUNDA: OBLIGACIONES DE NO DIVULGACIÓN
La Parte Receptora se compromete a:
a) Tratar la Información Confidencial con el mismo grado de cuidado que emplea para la suya propia de similar naturaleza, pero nunca menor a un estándar razonable de diligencia.
b) No divulgar, copiar, publicar ni transferir la Información a ningún tercero sin la autorización previa y por escrito de la Parte Divulgadora.
c) Limitar el acceso a aquellos empleados, directores o asesores legales y financieros que tengan necesidad estricta de conocerla para evaluar el Proyecto.

CLÁUSULA TERCERA: DURACIÓN DEL SECRETO
Las obligaciones contenidas en el presente Acuerdo permanecerán en vigor durante un plazo de cinco (5) años contados a partir de la firma del presente instrumento, no obstante la finalización o descarte del Proyecto comercial.

CLÁUSULA CUARTA: PROHIBICIÓN DE NO CAPTACIÓN DE PERSONAL (NON-SOLICITATION)
Durante la vigencia de este acuerdo y por los dos (2) años siguientes a su término, ninguna de las partes podrá contratar directa o indirectamente ni inducir a abandonar su empleo a ningún trabajador o directivo de la contraparte involucrado en las evaluaciones del Proyecto.

CLÁUSULA QUINTA: PENALIDAD CONVENCIONAL POR INCUMPLIMIENTO
En caso de violación o divulgación no autorizada de la Información Confidencial, la parte infractora indemnizará los daños y perjuicios materiales causados y pagará además una cláusula penal compensatoria inmediata ascendente a la suma de USD 50,000.00 (cincuenta mil dólares de los Estados Unidos), sin perjuicio de las acciones judiciales y medidas cautelares urgentes.

CLÁUSULA SEXTA: JURISDICCIÓN
Este acuerdo se somete a la legislación mercantil ecuatoriana y a los jueces civiles competentes del cantón Guayaquil.

Suscrito en Guayaquil, a 10 de febrero de 2026.
"""

def create_docx(filename, title, content):
    doc = docx.Document()
    h = doc.add_heading(title, level=0)
    for p in content.strip().split("\n\n"):
        doc.add_paragraph(p.strip())
    path = os.path.join(EJEMPLOS_DIR, filename)
    doc.save(path)
    return path

def create_txt(filename, content):
    path = os.path.join(EJEMPLOS_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip())
    return path

if __name__ == "__main__":
    create_docx("Contrato_SaaS_CloudTech.docx", "CONTRATO DE SERVICIOS SAAS", saas_text)
    create_txt("Contrato_SaaS_CloudTech.txt", saas_text)
    create_docx("Acuerdo_Confidencialidad_NDA.docx", "ACUERDO DE CONFIDENCIALIDAD (NDA)", nda_text)
    create_txt("Acuerdo_Confidencialidad_NDA.txt", nda_text)
    print("Contratos de prueba generados exitosamente.")
