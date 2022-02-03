<!DOCTYPE html>
<html>
<head>

</head>
<body style="font-family: sans-serif;">

<h2>INFORME IMPORTACIÓ MASSIVA</h2>
<p id="intervals" style="font-size: 18px;">Amb interval de <strong>${interval['inici']}</strong> a <strong>${interval['final']}</strong></p>
<table style="border-collapse: collapse;width: 100%;border-bottom: 4px solid #bac92c;">
  <tr style="background-color: #bac92c;color: white;">
    <th style="border: 2px solid white;text-align: left;padding: 12px;">Portal</th>
    <th style="border: 2px solid white;text-align: left;padding: 12px;">Ha anat bé?</th>
    <th style="border: 2px solid white;text-align: left;padding: 12px;">Observacions</th>
  </tr>
% for crawler in success:
  <tr>
    <td style="border-bottom: 1px solid #bac92c;text-align: left;padding: 12px;">${crawler['name']}</td>
    <td style="border-bottom: 1px solid #bac92c;text-align: center;padding: 12px;"><img src="cid:image1" alt="Sí" style="width: 20px;"></td>
    <td style="border-bottom: 1px solid #bac92c;text-align: left;padding: 12px;">${crawler['description']}</td>
  </tr>
% endfor
% for crawler in fail:
  <tr>
    <td style="border-bottom: 1px solid #bac92c;text-align: left;padding: 12px;">${crawler['name']}</td>
    <td style="border-bottom: 1px solid #bac92c;text-align: center;padding: 12px;"><img src="cid:image2" alt="No" style="width: 20px;"></td>
    <td style="border-bottom: 1px solid #bac92c;text-align: left;padding: 12px;">${crawler['description']}</td>
  </tr>
% endfor
</table>
<div id="resum" style="margin-top: 4px; padding: 12px;border-bottom: 2px solid #bac92c;">
  <p><strong>Importats correctament:</strong> ${len(success)}</p>
  <p><strong>No s'han pogut importar:</strong> ${len(fail)}</p>
</div>
</body>
</html>