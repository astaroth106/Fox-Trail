xof 0302txt 0032

template Header {
 <3D82AB43-62DA-11cf-AB39-0020AF71E433>
 WORD major;
 WORD minor;
 DWORD flags;
}

template Vector {
 <3D82AB5E-62DA-11cf-AB39-0020AF71E433>
 FLOAT x;
 FLOAT y;
 FLOAT z;
}

template Coords2d {
 <F6F23F44-7686-11cf-8F52-0040333594A3>
 FLOAT u;
 FLOAT v;
}

template Quaternion {
 <10DD46A3-775B-11cf-8F52-0040333594A3>
 FLOAT s;
 Vector v;
}

template Matrix4x4 {
 <F6F23F45-7686-11cf-8F52-0040333594A3>
 array FLOAT matrix[16];
}

template ColorRGBA {
 <35FF44E0-6C7C-11cf-8F52-0040333594A3>
 FLOAT red;
 FLOAT green;
 FLOAT blue;
 FLOAT alpha;
}

template ColorRGB {
 <D3E16E81-7835-11cf-8F52-0040333594A3>
 FLOAT red;
 FLOAT green;
 FLOAT blue;
}

template IndexedColor {
 <1630B820-7842-11cf-8F52-0040333594A3>
 DWORD index;
 ColorRGBA indexColor;
}

template Boolean {
 <4885AE61-78E8-11cf-8F52-0040333594A3>
 WORD truefalse;
}

template Boolean2d {
 <4885AE63-78E8-11cf-8F52-0040333594A3>
 Boolean u;
 Boolean v;
}

template MaterialWrap {
 <4885AE60-78E8-11cf-8F52-0040333594A3>
 Boolean u;
 Boolean v;
}

template TextureFilename {
 <A42790E1-7810-11cf-8F52-0040333594A3>
 STRING filename;
}

template Material {
 <3D82AB4D-62DA-11cf-AB39-0020AF71E433>
 ColorRGBA faceColor;
 FLOAT power;
 ColorRGB specularColor;
 ColorRGB emissiveColor;
 [...]
}

template MeshFace {
 <3D82AB5F-62DA-11cf-AB39-0020AF71E433>
 DWORD nFaceVertexIndices;
 array DWORD faceVertexIndices[nFaceVertexIndices];
}

template MeshFaceWraps {
 <4885AE62-78E8-11cf-8F52-0040333594A3>
 DWORD nFaceWrapValues;
 Boolean2d faceWrapValues;
}

template MeshTextureCoords {
 <F6F23F40-7686-11cf-8F52-0040333594A3>
 DWORD nTextureCoords;
 array Coords2d textureCoords[nTextureCoords];
}

template MeshMaterialList {
 <F6F23F42-7686-11cf-8F52-0040333594A3>
 DWORD nMaterials;
 DWORD nFaceIndexes;
 array DWORD faceIndexes[nFaceIndexes];
 [Material]
}

template MeshNormals {
 <F6F23F43-7686-11cf-8F52-0040333594A3>
 DWORD nNormals;
 array Vector normals[nNormals];
 DWORD nFaceNormals;
 array MeshFace faceNormals[nFaceNormals];
}

template MeshVertexColors {
 <1630B821-7842-11cf-8F52-0040333594A3>
 DWORD nVertexColors;
 array IndexedColor vertexColors[nVertexColors];
}

template Mesh {
 <3D82AB44-62DA-11cf-AB39-0020AF71E433>
 DWORD nVertices;
 array Vector vertices[nVertices];
 DWORD nFaces;
 array MeshFace faces[nFaces];
 [...]
}

template FrameTransformMatrix {
 <F6F23F41-7686-11cf-8F52-0040333594A3>
 Matrix4x4 frameMatrix;
}

template Frame {
 <3D82AB46-62DA-11cf-AB39-0020AF71E433>
 [...]
}

template FloatKeys {
 <10DD46A9-775B-11cf-8F52-0040333594A3>
 DWORD nValues;
 array FLOAT values[nValues];
}

template TimedFloatKeys {
 <F406B180-7B3B-11cf-8F52-0040333594A3>
 DWORD time;
 FloatKeys tfkeys;
}

template AnimationKey {
 <10DD46A8-775B-11cf-8F52-0040333594A3>
 DWORD keyType;
 DWORD nKeys;
 array TimedFloatKeys keys[nKeys];
}

template AnimationOptions {
 <E2BF56C0-840F-11cf-8F52-0040333594A3>
 DWORD openclosed;
 DWORD positionquality;
}

template Animation {
 <3D82AB4F-62DA-11cf-AB39-0020AF71E433>
 [...]
}

template AnimationSet {
 <3D82AB50-62DA-11cf-AB39-0020AF71E433>
 [Animation]
}

Mesh mesh0 {
	24;
	-65.435471;0.000000;-41.668819;,
	-65.435471;99.952309;-41.668819;,
	41.745838;0.000000;-41.668819;,
	41.745838;99.952309;-41.668819;,
	41.745838;0.000000;-41.668819;,
	41.745838;99.952309;-41.668819;,
	41.745838;0.000000;64.471893;,
	41.745838;99.952309;64.471893;,
	41.745838;0.000000;64.471893;,
	41.745838;99.952309;64.471893;,
	-65.435471;0.000000;64.471893;,
	-65.435471;99.952309;64.471893;,
	-65.435471;0.000000;64.471893;,
	-65.435471;99.952309;64.471893;,
	-65.435471;0.000000;-41.668819;,
	-65.435471;99.952309;-41.668819;,
	-65.435471;0.000000;-41.668819;,
	41.745838;0.000000;-41.668819;,
	41.745838;0.000000;64.471893;,
	-65.435471;0.000000;64.471893;,
	-65.435471;99.952309;-41.668819;,
	41.745838;99.952309;-41.668819;,
	41.745838;99.952309;64.471893;,
	-65.435471;99.952309;64.471893;;

	8;
	4;0;1;3;2;,
	4;4;5;7;6;,
	4;8;9;11;10;,
	4;12;13;15;14;,
	3;17;19;16;,
	3;19;17;18;,
	3;21;20;23;,
	3;23;22;21;;

	MeshNormals {
		24;
		0.000000;0.000000;-1.000000;,
		0.000000;0.000000;-1.000000;,
		0.000000;0.000000;-1.000000;,
		0.000000;0.000000;-1.000000;,
		1.000000;0.000000;0.000000;,
		1.000000;0.000000;0.000000;,
		1.000000;0.000000;0.000000;,
		1.000000;0.000000;0.000000;,
		0.000000;0.000000;1.000000;,
		0.000000;0.000000;1.000000;,
		0.000000;0.000000;1.000000;,
		0.000000;0.000000;1.000000;,
		-1.000000;0.000000;0.000000;,
		-1.000000;0.000000;0.000000;,
		-1.000000;0.000000;0.000000;,
		-1.000000;0.000000;0.000000;,
		-0.000000;-1.000000;-0.000000;,
		-0.000000;-1.000000;-0.000000;,
		-0.000000;-1.000000;-0.000000;,
		-0.000000;-1.000000;-0.000000;,
		0.000000;1.000000;0.000000;,
		0.000000;1.000000;0.000000;,
		0.000000;1.000000;0.000000;,
		0.000000;1.000000;0.000000;;

		8;
		4;0;1;3;2;,
		4;4;5;7;6;,
		4;8;9;11;10;,
		4;12;13;15;14;,
		3;17;19;16;,
		3;19;17;18;,
		3;21;20;23;,
		3;23;22;21;;
	}

	MeshTextureCoords  {
		24;
		0.000000;1.000000;,
		0.000000;0.339940;,
		0.251220;1.000000;,
		0.251220;0.339940;,
		0.251220;1.000000;,
		0.251220;0.339940;,
		0.500000;1.000000;,
		0.500000;0.339940;,
		0.500000;1.000000;,
		0.500000;0.339940;,
		0.751220;1.000000;,
		0.751220;0.339940;,
		0.751220;1.000000;,
		0.751220;0.339940;,
		1.000000;1.000000;,
		1.000000;0.339940;,
		0.000000;0.000000;,
		0.251220;0.000000;,
		0.251220;0.339940;,
		0.000000;0.339940;,
		0.748780;0.339940;,
		1.000000;0.339940;,
		1.000000;0.000000;,
		0.748780;0.000000;;

	}

	MeshMaterialList {
		1;
		8;
		0,
		0,
		0,
		0,
		0,
		0,
		0,
		0;;
		Material N {
			1.000000;1.000000;1.000000;1.000000;;
			0;
			0.000000;0.000000;0.000000;;
			0.000000;0.000000;0.000000;;
				TextureFilename  {
				"spacebackground.jpg";
				}

			}
		}
	}

