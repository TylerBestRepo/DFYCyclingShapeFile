import csv
import osgeo.ogr as ogr
import osgeo.osr as osr
import datetime

driver = ogr.GetDriverByName("ESRI Shapefile")
data_source = driver.CreateDataSource(r"E:\UNI\Research_assistant\Shape files\Ride 3\Ride_3.shp")
srs = osr.SpatialReference()
srs.ImportFromEPSG(4326)

# create the layer
layer = data_source.CreateLayer("Ride_3", srs, ogr.wkbPoint)

# Add the fields we're interested in
field_name = ogr.FieldDefn("Speed", ogr.OFTReal)
field_name.SetWidth(24)
layer.CreateField(field_name)
layer.CreateField(ogr.FieldDefn("Latitude", ogr.OFTReal))
layer.CreateField(ogr.FieldDefn("Longitude", ogr.OFTReal))
layer.CreateField(ogr.FieldDefn("Distance", ogr.OFTReal))
layer.CreateField(ogr.FieldDefn("Cadence", ogr.OFTReal))
layer.CreateField(ogr.FieldDefn("Altitude", ogr.OFTReal))

# Save and close the data source

with open(r"E:\UNI\Research_assistant\WAHOO files\Oct-31.csv") as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    for row in csv_reader:
        if row[2] == 'record' and row[0] == 'Data' and len(row) > 20:
            position_lat_semi_circles = row[7]
            position_long_semi_circles = row[10]
            speed = row[28]
            cadence = row[25]
            distance = row[22]
            altitude = row[16]
            time = row[4]

            if len(position_lat_semi_circles) > 1:  # This is needed because the first measurement i pulled contained no values so I'm essentially doing all this to ignore the first reading or any null readigns
                position_lat_degrees = float(position_lat_semi_circles) * (180 / 2**31)
                position_long_degrees = float(position_long_semi_circles) * (180 / 2 ** 31)
                print(f"position_lat_degrees: {position_lat_degrees}")
                print(f"position_long_degrees: {position_long_degrees}\n")
                print(f"Speed: {speed}\n")
                #We want to convert speed from a string to a number value
                if len(speed) < 1:
                    speed = "0"
                speed = float(speed)
                time = float(time)
                timestamp = datetime.datetime.fromtimestamp(time)
                print(timestamp.strftime('%M:%S')) #This timestamp comes out as a string, before this conversion it is some sort of time object
                print(type(timestamp.strftime('%M:%S')))

                # create the feature
                feature = ogr.Feature(layer.GetLayerDefn())
                # Set the attributes using the values from the delimited text file
                feature.SetField("Speed", speed)
                #feature.SetField("Time Elapsed", time)
                feature.SetField("Latitude", position_lat_degrees)
                feature.SetField("Longitude", position_long_degrees)
                feature.SetField("Cadence", cadence)
                feature.SetField("Distance", distance)
                feature.SetField("Altitude", altitude)

                # create the WKT for the feature using Python string formatting
                wkt = f"POINT({position_long_degrees} {position_lat_degrees})"
                #print("wkt: {}".format(wkt))

                # Create the point from the Well Known Txt
                point = ogr.CreateGeometryFromWkt(wkt)
                feature.SetGeometry(point)
                layer.CreateFeature(feature)

                feature = None
    data_source = None