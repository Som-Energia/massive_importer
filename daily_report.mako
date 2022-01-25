<!DOCTYPE html>
<html>
<head>
<style>
table {
  font-family: arial, sans-serif;
  border-collapse: collapse;
  width: 100%;
}

td, th {
  border: 1px solid #dddddd;
  text-align: left;
  padding: 8px;
}

tr:nth-child(even) {
  background-color: #dddddd;
}
</style>
</head>
<body>

<h2>Importació massiva</h2>

<table>
  <tr>
    <th>Portal</th>
    <th>Ha anat bé?</th>
    <th>Observacions</th>
  </tr>
% for crawler in crawlers:
  <tr>
    <td>${crawler['name']}</td>
    <td>${crawler['success']}</td>
    <td>${crawler['description']}</td>
  </tr>
% endfor
  <tr>
    <td>Magazzini Alimentari Riuniti</td>
    <td>Giovanni Rovelli</td>
    <td>Aiovanni Rovelli</td>
  </tr>
</table>

</body>
</html>


