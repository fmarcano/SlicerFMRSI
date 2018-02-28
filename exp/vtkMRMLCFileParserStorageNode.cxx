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

// MRML includes
#include "vtkMRMLCFileParserStorageNode.h"
#include "vtkMRMLStorableNode.h"
#include "vtkMRMLScene.h"

// VTK includes
#include <vtkObjectFactory.h>
#include <vtkStringArray.h>
#include <vtkBitArray.h>
#include <vtkNew.h>
//#include <vtkSmartPointer.h>
//#include <vtksys/SystemTools.hxx>

//------------------------------------------------------------------------------
vtkMRMLNodeNewMacro(vtkMRMLCFileParserStorageNode);

//----------------------------------------------------------------------------
vtkMRMLCFileParserStorageNode::vtkMRMLCFileParserStorageNode()
{
  this->FileName = 0;
  this->DefaultWriteFileExtension = ".7";
}

//----------------------------------------------------------------------------
vtkMRMLCFileParserStorageNode::~vtkMRMLCFileParserStorageNode()
{
}

//----------------------------------------------------------------------------
void vtkMRMLCFileParserStorageNode::PrintSelf(ostream& os, vtkIndent indent)
{
  vtkMRMLStorageNode::PrintSelf(os,indent);
}

//----------------------------------------------------------------------------
bool vtkMRMLCFileParserStorageNode::CanReadInReferenceNode(vtkMRMLNode *refNode)
{
  return refNode->IsA("vtkMRMLStorableNode");
}

//----------------------------------------------------------------------------
int vtkMRMLCFileParserStorageNode::ReadDataInternal(vtkMRMLNode *refNode)
{
  std::string fullName = this->GetFullNameFromFileName();

  if (fullName.empty())
    {
    vtkErrorMacro("ReadData: File name not specified");
    return 0;
    }
  vtkMRMLStorableNode *storableNode = vtkMRMLStorableNode::SafeDownCast(refNode);
  if (storableNode == NULL)
    {
    vtkErrorMacro("ReadData: unable to cast input node " << refNode->GetID() << " to a storable node");
    return 0;
    }

  // Check that the file exists
  if (vtksys::SystemTools::FileExists(fullName) == false)
    {
    vtkErrorMacro("ReadData: file '" << fullName << "' not found.");
    return 0;
    }

  /******* LOGICA DE LECTURA ******/
  
  vtkDebugMacro("ReadData: successfully read table from file: " << fullName);

  return 1;
}

//----------------------------------------------------------------------------
int vtkMRMLCFileParserStorageNode::WriteDataInternal(vtkMRMLNode *refNode)
{
  if (this->GetFileName() == NULL)
    {
    vtkErrorMacro("WriteData: file name is not set");
    return 0;
    }
  std::string fullName = this->GetFullNameFromFileName();
  if (fullName.empty())
    {
    vtkErrorMacro("WriteData: file name not specified");
    return 0;
    }

  vtkMRMLStorableNode *storableNode = vtkMRMLStorableNode::SafeDownCast(refNode);
  if (storableNode == NULL)
    {
    vtkErrorMacro("WriteData: unable to cast input node " << refNode->GetID() << " to a valid storable node");
    return 0;
    }
  if(!this->FileName || std::string(this->FileName).empty())
    {
    vtkErrorMacro(<<"No file name specified!");
    return 0;
    }

  /********* LOGICA DE ESCRITURA **************/
  
  if (!this->FileName || std::string(this->FileName).empty())
    {
    vtkErrorMacro("ReadData: no file name for the node '" << std::string(storableNode->GetName()));
    return 0;
    }

 

  vtkDebugMacro("WriteData: successfully wrote file: " << fullName);
  return 1;
}


//----------------------------------------------------------------------------
void vtkMRMLCFileParserStorageNode::InitializeSupportedReadFileTypes()
{
  this->SupportedReadFileTypes->InsertNextValue("GE PFile (.7)");
  //this->SupportedReadFileTypes->InsertNextValue("SQLight database (.db3)");
}

//----------------------------------------------------------------------------
void vtkMRMLCFileParserStorageNode::InitializeSupportedWriteFileTypes()
{
  this->SupportedWriteFileTypes->InsertNextValue("GE PFile (.7)");
  //this->SupportedWriteFileTypes->InsertNextValue("SQLight database (.db3)");
}