<!DOCTYPE html>
<html>
<head>
<style>

body {
  font-family: sans-serif;
}

table {
  border-collapse: collapse;
  width: 100%;
}

td, th {
  border: 2px solid white;
  text-align: left;
  padding: 12px;
}

tr:nth-child(odd) {
  background-color: #efefef;
}

tr:first-child {
  background-color: #bac92c;
  color: white;
}

#intervals {
  font-size: 18px;
}

tr:last-child td {
  border: 0px solid #bac92c;
}

table {
  border-bottom: 4px solid #bac92c;
}

td:nth-child(2) {
  text-align: center;
}

img {
  width: 20px;
}

div {
  padding: 12px;
  border-bottom: 2px solid #bac92c;
}

</style>
</head>
<body>

<h2>INFORME IMPORTACIÓ MASSIVA</h2>
<p id="intervals">Amb interval de <strong>${interval['inici']}</strong> a <strong>${interval['final']}</strong></p>
<table>
  <tr>
    <th>Portal</th>
    <th>Ha anat bé?</th>
    <th>Observacions</th>
  </tr>
% for crawler in success:
  <tr>
    <td>${crawler['name']}</td>
    <td><img src="./success.png" alt="Sí"/></td>
    <td>${crawler['description']}</td>
  </tr>
% endfor
% for crawler in fail:
  <tr>
    <td>${crawler['name']}</td>
    <td><img src="./fail.png" alt="No"/></td>
    <td>${crawler['description']}</td>
  </tr>
% endfor
</table>
<div>
  <p><strong>Importats correctament:</strong> ${len(success)}</p>
  <p><strong>No s'han pogut importar:</strong> ${len(fail)}</p>
</div>
</body>
</html>


