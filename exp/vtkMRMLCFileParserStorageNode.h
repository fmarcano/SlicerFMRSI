/*==============================================================================

  Program: 3D Slicer

  Portions (c) Copyright 2018 Brigham and Women's Hospital (BWH) All Rights Reserved.

  See COPYRIGHT.txt
  or http://www.slicer.org/copyright/copyright.txt for details.

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.

  This file was originally developed by Francisco Marcano, Universidad de La Laguna, Tenerife, Spain.

==============================================================================*/

#ifndef __vtkMRMLCFileParserStorageNode_h
#define __vtkMRMLCFileParserStorageNode_h

#include "vtkMRMLStorageNode.h"


class VTK_MRML_EXPORT vtkMRMLCFileParserStorageNode : public vtkMRMLStorageNode
{
public:
  static vtkMRMLCFileParserStorageNode *New();
  vtkTypeMacro(vtkMRMLCFileParserStorageNode,vtkMRMLStorageNode);
  void PrintSelf(ostream& os, vtkIndent indent) VTK_OVERRIDE;

  virtual vtkMRMLNode* CreateNodeInstance() VTK_OVERRIDE;

  /// Get node XML tag name (like Storage, Model)
  virtual const char* GetNodeTagName() VTK_OVERRIDE {return "CFileParserStorage";}

  /// Return true if the node can be read in
  virtual bool CanReadInReferenceNode(vtkMRMLNode *refNode) VTK_OVERRIDE;


  /// FileName
  vtkSetStringMacro(FileName);
  vtkGetStringMacro(FileName);


protected:
  vtkMRMLCFileParserStorageNode();
  ~vtkMRMLCFileParserStorageNode();
  vtkMRMLCFileParserStorageNode(const vtkMRMLCFileParserStorageNode&);
  void operator=(const vtkMRMLCFileParserStorageNode&);

  /// Initialize all the supported write file types
  virtual void InitializeSupportedReadFileTypes() VTK_OVERRIDE;

  /// Initialize all the supported write file types
  virtual void InitializeSupportedWriteFileTypes() VTK_OVERRIDE;

  /// Read data and set it in the referenced node. Returns 0 on failure.
  virtual int ReadDataInternal(vtkMRMLNode *refNode) VTK_OVERRIDE;

  /// Write data from a  referenced node. Returns 0 on failure.
  virtual int WriteDataInternal(vtkMRMLNode *refNode) VTK_OVERRIDE;

  char *FileName;
};

#endif