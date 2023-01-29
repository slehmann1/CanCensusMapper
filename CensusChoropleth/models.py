from django.db import models


class GeoLevel(models.Model):
    # ['Country', 'Province', 'Census division', 'Census subdivision','Territory']
    name = models.CharField(max_length=20, blank=False, null=False)

    def __str__(self) -> str:
        return f"{self.name}"


class Geography(models.Model):
    dguid = models.CharField(max_length=14, blank=False, null=False)
    geo_name = models.CharField(max_length=25, blank=False, null=False)
    geo_level = models.ForeignKey(
        GeoLevel, on_delete=models.CASCADE, blank=False, null=False)
    geometry = models.TextField(blank=True)

    def __str__(self) -> str:
        return f"{self.geo_name} - {self.dguid} - {self.geo_level}"

    def set_geometry(self, geometry):
        self.geometry = geometry


class Characteristic(models.Model):
    char_name = models.CharField(max_length=100, blank=False, null=False)

    def __str__(self) -> str:
        return f"{self.char_name}"


class Datum(models.Model):
    geo = models.ForeignKey(
        Geography, on_delete=models.CASCADE, blank=False, null=False)
    characteristic = models.ForeignKey(
        Characteristic, on_delete=models.CASCADE, blank=False, null=False)
    value = models.FloatField(blank=True, null=True)

    def __str__(self) -> str:
        return f"Value: {self.value} Geo: {self.geo} Characteristic: {self.characteristic}"
