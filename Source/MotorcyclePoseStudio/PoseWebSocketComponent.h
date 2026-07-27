#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "IWebSocket.h"
#include "PoseWebSocketComponent.generated.h"

USTRUCT()
struct FRiderState
{
    GENERATED_BODY()

    float LeftElbow = 0.0f;
    float RightElbow = 0.0f;
    float LeftKnee = 0.0f;
    float RightKnee = 0.0f;
    float LeftFoot = 0.0f;
    float RightFoot = 0.0f;
    float TorsoAngle = 0.0f;
    float PoseConfidence = 0.0f;
};

UCLASS(ClassGroup = (Custom), meta = (BlueprintSpawnableComponent))
class MOTORCYCLEPOSESTUDIO_API UPoseWebSocketComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UPoseWebSocketComponent();

protected:
    virtual void BeginPlay() override;

public:
    virtual void TickComponent(
        float DeltaTime,
        ELevelTick TickType,
        FActorComponentTickFunction* ThisTickFunction
    ) override;

private:
    TSharedPtr<IWebSocket> WebSocket;

    void Connect();

    void HandleConnected();
    void HandleConnectionError(const FString& Error);
    void HandleClosed(
        int32 StatusCode,
        const FString& Reason,
        bool bWasClean
    );
    void HandleMessage(const FString& Message);
    bool ParseRiderState(
        const FString& Message,
        FRiderState& OutRiderState
    ) const;
};