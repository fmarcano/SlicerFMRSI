/*==============================================================================

  Program: 3D Slicer

  Copyright (c) Kitware Inc.

  See COPYRIGHT.txt
  or http://www.slicer.org/copyright/copyright.txt for details.

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.

  This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
  and was partially funded by NIH grant 3P41RR013218-12S1

==============================================================================*/

// FooBar Widgets includes
#include "qSlicerCFileParserFooBarWidget.h"
#include "ui_qSlicerCFileParserFooBarWidget.h"

//-----------------------------------------------------------------------------
/// \ingroup Slicer_QtModules_CFileParser
class qSlicerCFileParserFooBarWidgetPrivate
  : public Ui_qSlicerCFileParserFooBarWidget
{
  Q_DECLARE_PUBLIC(qSlicerCFileParserFooBarWidget);
protected:
  qSlicerCFileParserFooBarWidget* const q_ptr;

public:
  qSlicerCFileParserFooBarWidgetPrivate(
    qSlicerCFileParserFooBarWidget& object);
  virtual void setupUi(qSlicerCFileParserFooBarWidget*);
};

// --------------------------------------------------------------------------
qSlicerCFileParserFooBarWidgetPrivate
::qSlicerCFileParserFooBarWidgetPrivate(
  qSlicerCFileParserFooBarWidget& object)
  : q_ptr(&object)
{
}

// --------------------------------------------------------------------------
void qSlicerCFileParserFooBarWidgetPrivate
::setupUi(qSlicerCFileParserFooBarWidget* widget)
{
  this->Ui_qSlicerCFileParserFooBarWidget::setupUi(widget);
}

//-----------------------------------------------------------------------------
// qSlicerCFileParserFooBarWidget methods

//-----------------------------------------------------------------------------
qSlicerCFileParserFooBarWidget
::qSlicerCFileParserFooBarWidget(QWidget* parentWidget)
  : Superclass( parentWidget )
  , d_ptr( new qSlicerCFileParserFooBarWidgetPrivate(*this) )
{
  Q_D(qSlicerCFileParserFooBarWidget);
  d->setupUi(this);
}

//-----------------------------------------------------------------------------
qSlicerCFileParserFooBarWidget
::~qSlicerCFileParserFooBarWidget()
{
}
