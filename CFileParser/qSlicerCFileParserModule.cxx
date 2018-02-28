/*==============================================================================

  Program: 3D Slicer

  Portions (c) Copyright Brigham and Women's Hospital (BWH) All Rights Reserved.

  See COPYRIGHT.txt
  or http://www.slicer.org/copyright/copyright.txt for details.

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.

==============================================================================*/

// CFileParser Logic includes
#include <vtkSlicerCFileParserLogic.h>

// CFileParser includes
#include "qSlicerCFileParserModule.h"
#include "qSlicerCFileParserModuleWidget.h"

//-----------------------------------------------------------------------------
#if (QT_VERSION < QT_VERSION_CHECK(5, 0, 0))
#include <QtPlugin>
Q_EXPORT_PLUGIN2(qSlicerCFileParserModule, qSlicerCFileParserModule);
#endif

//-----------------------------------------------------------------------------
/// \ingroup Slicer_QtModules_ExtensionTemplate
class qSlicerCFileParserModulePrivate
{
public:
  qSlicerCFileParserModulePrivate();
};

//-----------------------------------------------------------------------------
// qSlicerCFileParserModulePrivate methods

//-----------------------------------------------------------------------------
qSlicerCFileParserModulePrivate::qSlicerCFileParserModulePrivate()
{
}

//-----------------------------------------------------------------------------
// qSlicerCFileParserModule methods

//-----------------------------------------------------------------------------
qSlicerCFileParserModule::qSlicerCFileParserModule(QObject* _parent)
  : Superclass(_parent)
  , d_ptr(new qSlicerCFileParserModulePrivate)
{
}

//-----------------------------------------------------------------------------
qSlicerCFileParserModule::~qSlicerCFileParserModule()
{
}

//-----------------------------------------------------------------------------
QString qSlicerCFileParserModule::helpText() const
{
  return "This is a loadable module that can be bundled in an extension";
}

//-----------------------------------------------------------------------------
QString qSlicerCFileParserModule::acknowledgementText() const
{
  return "This work was partially funded by NIH grant NXNNXXNNNNNN-NNXN";
}

//-----------------------------------------------------------------------------
QStringList qSlicerCFileParserModule::contributors() const
{
  QStringList moduleContributors;
  moduleContributors << QString("John Doe (AnyWare Corp.)");
  return moduleContributors;
}

//-----------------------------------------------------------------------------
QIcon qSlicerCFileParserModule::icon() const
{
  return QIcon(":/Icons/CFileParser.png");
}

//-----------------------------------------------------------------------------
QStringList qSlicerCFileParserModule::categories() const
{
  return QStringList() << "fMRSI";
}

//-----------------------------------------------------------------------------
QStringList qSlicerCFileParserModule::dependencies() const
{
  return QStringList();
}

//-----------------------------------------------------------------------------
void qSlicerCFileParserModule::setup()
{
  this->Superclass::setup();
}

//-----------------------------------------------------------------------------
qSlicerAbstractModuleRepresentation* qSlicerCFileParserModule
::createWidgetRepresentation()
{
  return new qSlicerCFileParserModuleWidget;
}

//-----------------------------------------------------------------------------
vtkMRMLAbstractLogic* qSlicerCFileParserModule::createLogic()
{
  return vtkSlicerCFileParserLogic::New();
}
